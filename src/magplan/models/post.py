import datetime
import enum
import hashlib
import logging
import mimetypes
import os
import typing as tp
import urllib
from typing import List

import django
import requests
from botocore.exceptions import ClientError
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import JSONField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from magplan.conf import settings as config
from magplan.integrations.images import S3Client
from magplan.integrations.posts import replace_images_paths, update_ext_db_xmd
from magplan.models.abc import AbstractSiteModel, AbstractBase
from magplan.models.issue import Issue
from magplan.models.section import Section
from magplan.models.stage import Stage
from magplan.models.user import User
from magplan.xmd import render_md
from magplan.xmd.mappers import s3_public_mapper as s3_image_mapper, plan_internal_mapper as plan_image_mapper

WP_DATE_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
S3_STATIC_BASE_PATH = os.environ.get("S3_STATIC_BASE_PATH")
logger = logging.getLogger()


class StorageType(enum.Enum):
    S3 = 1


class Post(AbstractSiteModel, AbstractBase):
    # Used for external parser configuration
    PAYWALL_NOTICE_HEAD = '<div class="paywall-notice">'
    PAYWALL_NOTICE_BODY = "Продолжение статьи доступно только продписчикам"
    PAYWALL_NOTICE_TAIL = "</div>"
    PAYWALL_NOTICE_RENDERED = "{}{}{}".format(
        PAYWALL_NOTICE_HEAD, PAYWALL_NOTICE_BODY, PAYWALL_NOTICE_TAIL
    )

    @property
    def full_title(self) -> str:
        if self.kicker is None:
            return self.title

        separator = " " if self.kicker.endswith(("!", ":", "?")) else ". "
        return f"{self.kicker}{separator}{self.title}"

    def __str__(self) -> str:
        return self.full_title

    POST_FORMAT_DEFAULT = 0
    POST_FORMAT_FEATURED = 1
    POST_FORMAT_CHOICES = (
        (POST_FORMAT_DEFAULT, "Default"),
        (POST_FORMAT_FEATURED, "Featured"),
    )

    format = models.SmallIntegerField(
        choices=POST_FORMAT_CHOICES, default=POST_FORMAT_DEFAULT
    )

    POST_FEATURES_DEFAULT = 0
    POST_FEATURES_ARCHIVE = 1
    POST_FEATURES_ADVERT = 2
    POST_FEATURES_TRANSLATED = 2
    POST_FEATURES_CHOICES = (
        (POST_FEATURES_DEFAULT, "Default"),
        (POST_FEATURES_ARCHIVE, "Archive"),
        (POST_FEATURES_ADVERT, "Advert"),
        (POST_FEATURES_TRANSLATED, "Translated"),
    )
    features = models.SmallIntegerField(
        choices=POST_FEATURES_CHOICES, default=POST_FEATURES_DEFAULT
    )

    finished_at = models.DateTimeField(
        null=False,
        blank=False,
        default=django.utils.timezone.now,
        verbose_name="Дедлайн",
    )
    published_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата публикации"
    )
    kicker = models.CharField(null=True, blank=True, max_length=255)
    slug = models.SlugField(
        null=True, blank=True, max_length=255, verbose_name="Слаг для URL"
    )
    title = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Заголовок статьи"
    )
    description = models.TextField(
        null=False, blank=True, verbose_name="Описание статьи"
    )
    views = models.IntegerField(default=0)
    is_paywalled = models.BooleanField(default=False)
    xmd = models.TextField(null=True)
    html = models.TextField(null=True)

    editor = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name="edited",
        verbose_name="Редактор",
    )
    authors = models.ManyToManyField(User, verbose_name="Авторы")
    stage = models.ForeignKey(
        Stage, on_delete=models.CASCADE, verbose_name="Этап"
    )
    issues = models.ManyToManyField(
        Issue, related_name="posts", verbose_name="Выпуски"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name="Раздел",
    )
    last_updater = models.ForeignKey(
        User,
        related_name="posts_updated",
        verbose_name="Кто последний обновлял",
        null=True,
        on_delete=models.SET_NULL,
    )

    meta = JSONField(default=dict)

    comments = GenericRelation("Comment")
    is_locked = models.BooleanField(default=False)
    css = models.TextField(
        null=True,
        blank=True,
        verbose_name="CSS-стили для статьи",
        help_text=("CSS, который будет применяться к превью статьи"),
    )

    def imprint_updater(self, user: User) -> None:
        """Update updated_at timestamp and set provided user as last_updater.

        `created_at` may be overwritten further on DB-hook level.
        .save() method should be explicitly called.
        """
        self.last_updater = user
        self.updated_at = datetime.datetime.now()

    @property
    def images(self):
        return list(
            filter(
                lambda a: a.type == Attachment.TYPE_IMAGE,
                self.attachment_set.all(),
            )
        )

    @property
    def pdfs(self):
        return list(
            filter(
                lambda a: a.type == Attachment.TYPE_PDF,
                self.attachment_set.all(),
            )
        )

    @property
    def files(self):
        return list(
            filter(
                lambda a: a.type == Attachment.TYPE_FILE,
                self.attachment_set.all(),
            )
        )

    @property
    def featured_image(self) -> tp.Optional["Attachment"]:
        return self.attachment_set.filter(
            type=Attachment.TYPE_FEATURED_IMAGE
        ).first()

    @property
    def assignee(self):
        if self.stage and self.stage.assignee:
            return self.stage.assignee
        elif self.editor:
            return self.editor
        else:
            return None

    @property
    def prev_stage_assignee(self):
        if self.stage.prev_stage and self.stage.prev_stage.assignee:
            return self.stage.prev_stage.assignee
        else:
            return self.editor

    @property
    def next_stage_assignee(self):
        if self.stage.next_stage and self.stage.next_stage.assignee:
            return self.stage.next_stage.assignee
        else:
            return self.editor

    @property
    def comments_(self):
        return self.comments.order_by("created_at").all

    @property
    def has_text(self):
        return self.xmd is not None and self.xmd != ""

    @property
    def is_default(self):
        return self.features == self.POST_FEATURES_DEFAULT

    @property
    def is_archive(self):
        return self.features == self.POST_FEATURES_ARCHIVE

    @property
    def is_advert(self):
        return self.features == self.POST_FEATURES_ADVERT

    @property
    def is_regular(self):
        return self.section.is_whitelisted == True

    @property
    def is_translated(self):
        return self.features == self.POST_FEATURES_TRANSLATED

    class Meta:
        permissions = (
            ("recieve_post_email_updates", "Recieve email updates for Post"),
            ("edit_extended_post_attrs", "Edit extended Post attributes"),
            # Direct article creation
            ("create_generic_post", "Create generic post"),
            ("create_archive_post", "Create archive post"),
            ("create_advert_post", "Create advert post"),
            ("create_regular_post", "Create regular post"),
            ("create_translated_post", "Create translated post"),
        )

    @property
    def is_overdue(self):
        if self.stage.slug in ("vault", "published"):
            return False
        return timezone.now() > self.finished_at

    @property
    def description_html(self):
        return render_md(self.description, render_lead=False)

    @property
    def wp_id(self):
        return self.meta.get("wpid")

    @property
    def lead(self) -> str:
        if not self.xmd:
            return ""

        paragraphs: List[str] = self.xmd.split("\n")
        for paragraph in paragraphs:
            cleaned_paragraph = paragraph.strip()
            if not cleaned_paragraph:
                continue

            if cleaned_paragraph.startswith("$"):
                cleaned_paragraph = cleaned_paragraph[1:]

            cleaned_paragraph = cleaned_paragraph.strip()
            return cleaned_paragraph

        return ""

    def build_xmd_blob(self, prepared_xmd: str) -> str:
        """Attaches CSS to XMD for remote CMS

        >>> self.css ='foo'
        'foo'

        >>> xmd = 'bar'
        'bar'

        >>> self.build_xmd_blob(self.xmd)
        %style type=text/css
        foo
        %style
        bar
        """
        OPENING_STYLE_TAG = "%style type=text/css"
        CLOSING_STYLE_TAG = "%style"

        if not prepared_xmd:
            return prepared_xmd

        if not self.css:
            return prepared_xmd

        return "{}\n{}\n{}\n{}".format(
            OPENING_STYLE_TAG, self.css, CLOSING_STYLE_TAG, prepared_xmd
        )

    def upload(self):
        """Uploads post, metadata and attachments to remote CMS

        * self images uploaded to S3.
        * self content uploaded to WP with uploaded S3 images urls

        This method is long-running, can cause time-outs
        and should be run ONLY in async tasks with post lock.

            with Lock():
                post.upload()
        """
        logger.debug("Staring Post.upload")
        if not self.wp_id:
            logger.warning("No wp_id, exiting")
            return

        for image in self.images:
            image.upload_to_storage()
        logger.debug("Uploaded images")

        # Upload to external DB
        prepared_xmd = replace_images_paths(
            xmd=self.xmd,
            attachments=self.images,
            mapper=s3_image_mapper,
        )
        logger.debug("Replaced images paths")

        upload_kwargs: tp.Dict[str, str] = {
            "xmd": prepared_xmd,
            "title": str(self),
            "css": self.css,
        }
        logger.debug("Prepared upload kwargs")

        if self.published_at and self.features == self.POST_FEATURES_ARCHIVE:
            logger.debug(
                "Running on archived post. Adding issues datetimes as publication dates"
            )
            post_date_gmt: str = self.published_at.strftime(
                WP_DATE_FORMAT_STRING
            )
            post_date: str = self.published_at.astimezone().strftime(
                WP_DATE_FORMAT_STRING
            )

            upload_kwargs["post_date_gmt"] = post_date_gmt
            upload_kwargs["post_date"] = post_date
            logger.debug("Added publication dates")

        logger.debug("Ready to run upload to WP")
        update_ext_db_xmd(self.wp_id, **upload_kwargs)

    def render_xmd(self):
        if not self.has_text:
            return

        prepared_xmd: str = replace_images_paths(
            self.xmd, self.images, mapper=plan_image_mapper
        )
        self.html = _render_with_external_parser(
            self.id,
            prepared_xmd,
            paywall_tag_html=Post.PAYWALL_NOTICE_RENDERED,
        )

        if not self.html:
            self.html = render_md(self.xmd, attachments=self.images)

        if Post.PAYWALL_NOTICE_HEAD in self.html:
            self.is_paywalled = True
        else:
            self.is_paywalled = False


class Attachment(AbstractBase):
    TYPE_IMAGE = 0
    TYPE_PDF = 1
    TYPE_FILE = 2
    TYPE_FEATURED_IMAGE = 3
    TYPE_CHOICES = (
        (TYPE_IMAGE, "Image"),
        (TYPE_PDF, "PDF"),
        (TYPE_FILE, "File"),
        (TYPE_FEATURED_IMAGE, "Featured image"),
    )
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_IMAGE)

    original_filename = models.CharField(
        null=False, blank=False, max_length=255
    )
    file = models.FileField(upload_to="attachments/%Y/%m/%d/", max_length=2048)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    meta = JSONField(default=dict)

    @property
    def s3_full_url(self):
        return "{}/{}".format(S3_STATIC_BASE_PATH, self.build_s3_object_path())

    def build_s3_object_path(self) -> str:
        """Returns S3 object key path for upload with trailing slash"""
        dirname = os.path.dirname(self.file.name)
        basename = os.path.basename(self.file.name)
        hashed_dirname = hashlib.md5(dirname.encode()).hexdigest()

        return "images/{}/{}/{}".format(hashed_dirname, self.id, basename)

    def _guess_self_mimetype(self) -> tp.Optional[str]:
        try:
            return mimetypes.guess_type(self.file.path, strict=False)[0]
        except ValueError as exc:
            return None

    def _upload_to_s3(self):
        with S3Client() as (s3, S3_BUCKET_NAME):
            object_path = self.build_s3_object_path()
            try:
                s3_object = s3.Object(S3_BUCKET_NAME, object_path)
                s3_object.upload_file(
                    self.file.path,
                    ExtraArgs={
                        "ACL": "public-read",
                        "ContentType": self._guess_self_mimetype(),
                    },
                )
            except ClientError as e:
                logging.error(e)
                return False
            return True

    def upload_to_storage(
        self, storage_type: StorageType = StorageType.S3
    ) -> None:
        if storage_type == StorageType.S3:
            self._upload_to_s3()


def _render_with_external_parser(
    id: int, xmd: str, paywall_tag_html: str = Post.PAYWALL_NOTICE_RENDERED
) -> tp.Optional[str]:
    FAILBACK_SYNTAX_LANG = "cpp"

    if not xmd:
        return None

    if not config.EXTERNAL_PARSER_URL:
        return None

    try:
        request_payload: tp.Dict[str, str] = {
            "id": id,
            "md": xmd,
            "lang": FAILBACK_SYNTAX_LANG,
            "xakepcut": paywall_tag_html,
        }
        request_headers: tp.Dict[str, str] = {  # unusued
            "content-type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        request_query_params: tp.Dict[str, str] = {
            "x": config.EXTERNAL_PARSER_TOKEN or ""
        }

        query_string = urllib.parse.urlencode(request_query_params)
        prepared_url = f"{config.EXTERNAL_PARSER_URL}?{query_string}"
        response = requests.post(prepared_url, data=request_payload)
        return response.text

    except Exception as exc:
        # TODO: add logger, no need to handle
        return None


@receiver(pre_save, sender=Post)
def on_post_pre_save(sender, instance: Post, **kwargs):
    instance.render_xmd()

    # If we're modifying existing object, not creating a new one
    if not instance._state.adding:
        if instance.features == Post.POST_FEATURES_ARCHIVE:
            if instance.issues.count():
                target_issue: Issue = instance.issues.first()

                # Convert date to datetime
                published_date: datetime.date = target_issue.published_at
                published_datetime: datetime.datetime = (
                    datetime.datetime.combine(
                        published_date, datetime.datetime.min.time()
                    )
                )
                instance.published_at = published_datetime
