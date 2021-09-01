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
import html2text
import requests
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Q, QuerySet
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import timezone

from magplan.conf import settings as  config
from magplan.integrations.images import S3Client
from magplan.integrations.posts import replace_images_paths, update_ext_db_xmd
from magplan.xmd import render_md
from magplan.xmd.mappers import s3_public_mapper as s3_image_mapper

NEW_IDEA_NOTIFICATION_PREFERENCE_NAME = 'magplan__new_idea_notification'
WP_DATE_FORMAT_STRING = '%Y-%m-%d %H:%M:%S'

from .xmd.mappers import plan_internal_mapper as plan_image_mapper

UserModel = get_user_model()

logger = logging.getLogger()


class StorageType(enum.Enum):
    S3 = 1


class AbstractBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    _old_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True


def current_site_id() -> int:
    return settings.SITE_ID


class AbstractSiteModel(models.Model):
    """
    Support for multisite managers
    """
    site = models.ForeignKey(Site, on_delete=models.CASCADE, default=current_site_id)
    objects = models.Manager()
    on_current_site = CurrentSiteManager()

    class Meta:
        abstract = True

    @classmethod
    def on_site(cls, site: tp.Optional[Site]) -> QuerySet:
        if not site:
            return cls.objects

        return cls.objects.filter(site=site)


class User(UserModel):
    class Meta:
        proxy = True

    meta = JSONField(default=dict)

    def __str__(self):
        return self.display_name_default

    @property
    def display_name_default(self):
        p: Profile = self.profile
        if p.l_name and p.f_name:
            return '%s %s' % (p.f_name, p.l_name)
        elif p.n_name:
            return p.n_name
        else:
            return self.email

    @property
    def display_name_generic(self):
        p: Profile = self.profile
        if p.l_name_generic and p.f_name_generic:
            return '%s %s' % (p.f_name_generic, p.l_name_generic)
        elif p.n_name:
            return p.n_name
        else:
            return self.email

    @property
    def str_reverse(self):
        return self.__str__()

    @property
    def str_employee(self):
        return self.__str__()

    class Meta:
        permissions = (
            ("access_magplan", "Can access magplan"),
            ("manage_authors", "Can manage authors"),
        )

    def is_member(self, group_name: str) -> bool:
        """Check if user is member of group

        :param group_name: Group name to check user belongs to
        :return: True if a memeber, otherwise False
        """
        return self.groups.filter(name=group_name).exists()


class Profile(AbstractBase):
    is_public = models.BooleanField(null=False, blank=False, default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    f_name = models.CharField('Имя', max_length=255, blank=True, null=True)
    m_name = models.CharField('Отчество', max_length=255, blank=True, null=True)
    l_name = models.CharField('Фамилия', max_length=255, blank=True, null=True)
    n_name = models.CharField('Ник', max_length=255, blank=True, null=True)
    bio = models.TextField('Био', blank=True, null=True)

    # Global fields
    f_name_generic = models.CharField('Имя латинницей', max_length=255, blank=True, null=True)
    l_name_generic = models.CharField('Фамилия латинницей', max_length=255, blank=True, null=True)
    bio_generic = models.TextField('Био латинницей', blank=True, null=True)

    RUSSIA = 0
    UKRAINE = 1
    BELARUS = 2
    KAZAKHSTAN = 3
    COUNTRY_CHOICES = (
        (RUSSIA, 'Россия'),
        (UKRAINE, 'Украина'),
        (BELARUS, 'Беларусь'),
        (KAZAKHSTAN, 'Казахстан'),
    )
    country = models.SmallIntegerField(
        'Страна', choices=COUNTRY_CHOICES, default=RUSSIA
    )
    city = models.CharField('Город или поселок', max_length=255, blank=True, null=True)
    notes = models.TextField('Примечания', blank=True, null=True)


class Section(AbstractSiteModel, AbstractBase):
    def __str__(self):
        return self.title

    slug = models.SlugField(null=False, blank=False, max_length=255)
    title = models.CharField(null=False, blank=False, max_length=255)
    description = models.TextField(null=True, blank=False)
    sort = models.SmallIntegerField(null=False, blank=False, default=0)
    color = models.CharField(null=False, blank=False, default='000000', max_length=6)
    is_archived = models.BooleanField(null=False, blank=False, default=False)
    is_whitelisted = models.BooleanField(null=False, blank=False, default=False)


class Magazine(AbstractBase):
    slug = models.SlugField(null=False, blank=False, max_length=255)
    title = models.CharField(null=False, blank=False, max_length=255)
    description = models.TextField(null=False, blank=True)

    def __str__(self):
        return self.title


class Issue(AbstractSiteModel, AbstractBase):
    class Meta:
        ordering = ['-number']

    def __str__(self):
        return '%s #%s' % (self.magazine, self.number)

    number = models.SmallIntegerField(null=False, blank=False, default=0)
    title = models.CharField(null=True, blank=False, max_length=255)
    description = models.TextField(null=True, blank=False)
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE)
    published_at = models.DateField(
        null=False, blank=False, default=datetime.date.today
    )

    @property
    def full_title(self) -> str:
        return '{} #{} {}'.format(
            'Хакер', self.number, self.title or ''
        )


class Stage(AbstractSiteModel, AbstractBase):
    def __str__(self):
        return self.title

    slug = models.SlugField(null=False, blank=False, max_length=255)
    title = models.CharField(null=False, blank=False, max_length=255)
    sort = models.SmallIntegerField(null=False, blank=False, default=0)
    duration = models.SmallIntegerField(null=True, blank=True, default=1)
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    prev_stage = models.ForeignKey(
        'self', related_name='n_stage', null=True, blank=True, on_delete=models.CASCADE
    )
    next_stage = models.ForeignKey(
        'self', related_name='p_stage', null=True, blank=True, on_delete=models.CASCADE
    )
    skip_notification = models.BooleanField(null=False, blank=False, default=False)
    meta = JSONField(default=dict)


class Idea(AbstractSiteModel, AbstractBase):
    AUTHOR_TYPE_NO = 'NO'
    AUTHOR_TYPE_NEW = 'NW'
    AUTHOR_TYPE_EXISTING = 'EX'
    AUTHOR_TYPE_CHOICES = [
        (AUTHOR_TYPE_NO, 'Нет автора'),
        (AUTHOR_TYPE_NEW, 'Новый автор'),
        (AUTHOR_TYPE_EXISTING, 'Существующий автор(ы)'),
    ]
    title = models.CharField(
        null=False, blank=False, max_length=255, verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    approved = models.BooleanField(null=True)
    editor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='editor')
    post = models.OneToOneField(
        'Post', on_delete=models.SET_NULL, null=True, blank=True
    )
    comments = GenericRelation('Comment')
    author_type = models.CharField(
        max_length=2,
        choices=AUTHOR_TYPE_CHOICES,
        default=AUTHOR_TYPE_NO,
        verbose_name='Автор',
    )
    authors_new = models.CharField(
        max_length=255, null=True, blank=True, verbose_name='Новые автор'
    )
    authors = models.ManyToManyField(
        User, verbose_name='Авторы', related_name='authors', blank=True
    )

    def voted(self, user):
        vote = next((v for v in self.votes.all() if v.user_id == user.id), None)

        if vote:
            return True
        return False

    def _send_vote_notification(self, recipient: User) -> None:
        subject = f'Новая идея «{self.title}». Голосуйте!'

        context = {
            'idea': self,
            'APP_URL': os.environ.get('APP_URL')
        }
        message_html_content: str = render_to_string('email/new_idea.html', context)
        message_text_content: str = html2text.html2text(message_html_content)

        msg = EmailMultiAlternatives(subject, message_text_content, config.PLAN_EMAIL_FROM,
                                     [recipient.email])
        msg.attach_alternative(message_html_content, 'text/html')
        msg.send()

    def send_vote_notifications(self) -> None:
        active_users: tp.List[User] = User.objects.filter(is_active=True).exclude(id=self.editor_id)
        recipients: tp.List[User] = [
            user for user in active_users
            if user.preferences[NEW_IDEA_NOTIFICATION_PREFERENCE_NAME]
        ]

        for recipient in recipients:
            self._send_vote_notification(recipient)

    def __str__(self):
        return self.title

    class Meta:
        permissions = (
            ('edit_extended_idea_attrs', 'Edit extended Idea attributes'),
            ('recieve_idea_email_updates', 'Recieve email updates for Idea'),
        )

    @property
    def comments_(self):
        return self.comments.order_by('created_at').all

    @property
    def score(self):
        MAX_SCORE = 100

        all_scores = sum([v.score for v in self.votes.all()])
        max_scores = len(self.votes.all()) * MAX_SCORE

        return round(all_scores / max_scores * 100)

    @property
    def description_html(self):
        return render_md(self.description)


class Post(AbstractSiteModel, AbstractBase):
    # Used for external parser configuration
    PAYWALL_NOTICE_HEAD = '<div class="paywall-notice">'
    PAYWALL_NOTICE_BODY = 'Продолжение статьи доступно только продписчикам'
    PAYWALL_NOTICE_TAIL = '</div>'
    PAYWALL_NOTICE_RENDERED = '{}{}{}'.format(
        PAYWALL_NOTICE_HEAD, PAYWALL_NOTICE_BODY, PAYWALL_NOTICE_TAIL
    )

    @property
    def full_title(self) -> str:
        if self.kicker is None:
            return self.title

        separator = ' ' if self.kicker.endswith(('!', ':', '?')) else '. '
        return f'{self.kicker}{separator}{self.title}'

    def __str__(self) -> str:
        return self.full_title

    POST_FORMAT_DEFAULT = 0
    POST_FORMAT_FEATURED = 1
    POST_FORMAT_CHOICES = (
        (POST_FORMAT_DEFAULT, 'Default'),
        (POST_FORMAT_FEATURED, 'Featured'),
    )

    format = models.SmallIntegerField(
        choices=POST_FORMAT_CHOICES, default=POST_FORMAT_DEFAULT
    )

    POST_FEATURES_DEFAULT = 0
    POST_FEATURES_ARCHIVE = 1
    POST_FEATURES_ADVERT = 2
    POST_FEATURES_TRANSLATED = 2
    POST_FEATURES_CHOICES = (
        (POST_FEATURES_DEFAULT, 'Default'),
        (POST_FEATURES_ARCHIVE, 'Archive'),
        (POST_FEATURES_ADVERT, 'Advert'),
        (POST_FEATURES_TRANSLATED, 'Translated'),
    )
    features = models.SmallIntegerField(choices=POST_FEATURES_CHOICES,
                                        default=POST_FEATURES_DEFAULT)

    finished_at = models.DateTimeField(
        null=False,
        blank=False,
        default=django.utils.timezone.now,
        verbose_name='Дедлайн',
    )
    published_at = models.DateTimeField(
        null=True, blank=True, verbose_name='Дата публикации'
    )
    kicker = models.CharField(null=True, blank=True, max_length=255)
    slug = models.SlugField(null=True, blank=True, max_length=255, verbose_name='Слаг для URL')
    title = models.CharField(
        null=True, blank=True, max_length=255, verbose_name='Заголовок статьи'
    )
    description = models.TextField(
        null=False, blank=True, verbose_name='Описание статьи'
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
        verbose_name='Редактор',
    )
    authors = models.ManyToManyField(User, verbose_name='Авторы')
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, verbose_name='Этап')
    issues = models.ManyToManyField(Issue, related_name='posts', verbose_name='Выпуски')
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        verbose_name='Раздел',
    )
    last_updater = models.ForeignKey(
        User,
        related_name='posts_updated',
        verbose_name='Кто последний обновлял',
        null=True,
        on_delete=models.SET_NULL,
    )

    meta = JSONField(default=dict)

    comments = GenericRelation('Comment')
    is_locked = models.BooleanField(default=False)
    css = models.TextField(
        null=True, blank=True, verbose_name='CSS-стили для статьи',
        help_text=(
            'CSS, который будет применяться к превью статьи'
        )
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
            filter(lambda a: a.type == Attachment.TYPE_IMAGE, self.attachment_set.all())
        )

    @property
    def pdfs(self):
        return list(
            filter(lambda a: a.type == Attachment.TYPE_PDF, self.attachment_set.all())
        )

    @property
    def files(self):
        return list(
            filter(lambda a: a.type == Attachment.TYPE_FILE, self.attachment_set.all())
        )

    @property
    def featured_image(self) -> tp.Optional['Attachment']:
        return self.attachment_set.filter(type=Attachment.TYPE_FEATURED_IMAGE).first()

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
        return self.comments.order_by('created_at').all

    @property
    def has_text(self):
        return self.xmd is not None and self.xmd != ''

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
            ('recieve_post_email_updates', 'Recieve email updates for Post'),
            ('edit_extended_post_attrs', 'Edit extended Post attributes'),
            # Direct article creation
            ('create_generic_post', 'Create generic post'),
            ('create_archive_post', 'Create archive post'),
            ('create_advert_post', 'Create advert post'),
            ('create_regular_post', 'Create regular post'),
            ('create_translated_post', 'Create translated post'),
        )

    @property
    def is_overdue(self):
        if self.stage.slug in ('vault', 'published'):
            return False
        return timezone.now() > self.finished_at

    @property
    def description_html(self):
        return render_md(self.description, render_lead=False)

    @property
    def wp_id(self):
        return self.meta.get('wpid')

    @property
    def lead(self) -> str:
        if not self.xmd:
            return ''

        paragraphs: List[str] = self.xmd.split('\n')
        for paragraph in paragraphs:
            cleaned_paragraph = paragraph.strip()
            if not cleaned_paragraph:
                continue

            if cleaned_paragraph.startswith('$'):
                cleaned_paragraph = cleaned_paragraph[1:]

            cleaned_paragraph = cleaned_paragraph.strip()
            return cleaned_paragraph

        return ''

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
        OPENING_STYLE_TAG = '%style type=text/css'
        CLOSING_STYLE_TAG = '%style'

        if not prepared_xmd:
            return prepared_xmd

        if not self.css:
            return prepared_xmd

        return '{}\n{}\n{}\n{}'.format(
            OPENING_STYLE_TAG,
            self.css,
            CLOSING_STYLE_TAG,
            prepared_xmd
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
        logger.debug('Staring Post.upload')
        if not self.wp_id:
            logger.warning('No wp_id, exiting')
            return

        for image in self.images:
            image.upload_to_storage()
        logger.debug('Uploaded images')

        # Upload to external DB
        prepared_xmd = replace_images_paths(
            xmd=self.xmd,
            attachments=self.images,
            mapper=s3_image_mapper,
        )
        logger.debug('Replaced images paths')

        upload_kwargs: tp.Dict[str, str] = {
            'xmd': prepared_xmd,
            'title': str(self),
            'css': self.css,
        }
        logger.debug('Prepared upload kwargs')

        if self.published_at and self.features == self.POST_FEATURES_ARCHIVE:
            logger.debug('Running on archived post. Adding issues datetimes as publication dates')
            post_date_gmt: str = self.published_at.strftime(WP_DATE_FORMAT_STRING)
            post_date: str = self.published_at.astimezone().strftime(WP_DATE_FORMAT_STRING)

            upload_kwargs['post_date_gmt'] = post_date_gmt
            upload_kwargs['post_date'] = post_date
            logger.debug('Added publication dates')

        logger.debug('Ready to run upload to WP')
        update_ext_db_xmd(self.wp_id, **upload_kwargs)

    def render_xmd(self):
        if not self.has_text:
            return

        prepared_xmd: str = replace_images_paths(
            self.xmd, self.images, mapper=plan_image_mapper
        )
        self.html = _render_with_external_parser(
            self.id, prepared_xmd, paywall_tag_html=Post.PAYWALL_NOTICE_RENDERED
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
        (TYPE_IMAGE, 'Image'),
        (TYPE_PDF, 'PDF'),
        (TYPE_FILE, 'File'),
        (TYPE_FEATURED_IMAGE, 'Featured image'),
    )
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_IMAGE)

    original_filename = models.CharField(null=False, blank=False, max_length=255)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/', max_length=2048)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    meta = JSONField(default=dict)

    S3_BUCKET_URL = 'https://{}.s3.eu-central-1.amazonaws.com'.format(
        os.environ.get('S3_BUCKET_NAME', '')
    )

    @property
    def s3_full_url(self):
        return '{}/{}'.format(self.S3_BUCKET_URL, self._build_s3_path())

    def _build_s3_path(self) -> str:
        """Returns S3 object key path for upload.
        """
        dirname = os.path.dirname(self.file.name)
        basename = os.path.basename(self.file.name)
        hashed_dirname = hashlib.md5(dirname.encode()).hexdigest()

        return '{}/{}/{}'.format(
            hashed_dirname,
            self.id,
            basename
        )

    def _guess_self_mimetype(self) -> tp.Optional[str]:
        try:
            return mimetypes.guess_type(self.file.path, strict=False)[0]
        except ValueError as exc:
            return None

    def _upload_to_s3(self):
        with S3Client() as (s3, S3_BUCKET_NAME):
            object_name = self._build_s3_path()
            try:
                s3_object = s3.Object(S3_BUCKET_NAME, object_name)
                s3_object.upload_file(
                    self.file.path,
                    ExtraArgs={
                        'ACL': 'public-read',
                        'ContentType': self._guess_self_mimetype()
                    })
            except ClientError as e:
                logging.error(e)
                return False
            return True

    def upload_to_storage(self, storage_type: StorageType = StorageType.S3) -> None:
        if storage_type == StorageType.S3:
            self._upload_to_s3()


class Comment(AbstractBase):
    SYSTEM_ACTION_SET_STAGE = 5
    SYSTEM_ACTION_UPDATE = 10
    SYSTEM_ACTION_CHANGE_META = 15
    SYSTEM_ACTION_CHOICES = (
        (SYSTEM_ACTION_SET_STAGE, 'Set stage'),
        (SYSTEM_ACTION_UPDATE, 'Update'),
        (SYSTEM_ACTION_CHANGE_META, 'Change meta'),
    )

    TYPE_SYSTEM = 5
    TYPE_PRIVATE = 10
    TYPE_PUBLIC = 15
    TYPE_CHOICES = (
        (TYPE_SYSTEM, 'system'),
        (TYPE_PRIVATE, 'private'),
        (TYPE_PUBLIC, 'public'),
    )
    text = models.TextField(blank=True)
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_PRIVATE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    commentable = GenericForeignKey('content_type', 'object_id')
    meta = JSONField(default=dict)

    def __str__(self):
        return '%s, %s:%s...' % (self.user_id, self.type, self.text[0:50])

    @property
    def html(self):
        return render_md(self.text, render_lead=False)

    @property
    def changelog(self):
        try:
            md = '\n'.join(self.meta['comment']['changelog'])
        except Exception:
            md = ''

        return render_md(md, render_lead=False)


class Vote(AbstractBase):
    SCORE_0 = 0
    SCORE_25 = 25
    SCORE_50 = 50
    SCORE_75 = 75
    SCORE_100 = 100
    SCORE_CHOICES = (
        (SCORE_0, 'Против таких статей в «Хакере»'),
        (SCORE_25, 'Не верю, что выйдет хорошо'),
        (SCORE_50, 'Тема нормальная, но не для меня'),
        (SCORE_75, 'Почитал бы, встретив в журнале'),
        (SCORE_100, 'Ради таких статей мог бы подписаться'),
    )
    score = models.SmallIntegerField(choices=SCORE_CHOICES, default=SCORE_50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='votes')

    @property
    def score_humanized(self):
        return self.__class__.SCORE_CHOICES


def users_with_perm(perm_name: str, include_superuser: bool = True) -> List[User]:
    """Get all users by full permission name

    :param perm_name: permission name without app name
    :param include_superuser:
    :return:
    """
    return User.objects.filter(
        Q(is_superuser=include_superuser)
        | Q(user_permissions__codename=perm_name)
        | Q(groups__permissions__codename=perm_name)
    ).distinct()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def _render_with_external_parser(
        id: int, xmd: str, paywall_tag_html: str = Post.PAYWALL_NOTICE_RENDERED
) -> tp.Optional[str]:
    FAILBACK_SYNTAX_LANG = 'cpp'

    if not xmd:
        return None

    if not config.EXTERNAL_PARSER_URL:
        return None

    try:
        request_payload: tp.Dict[str, str] = {
            'id': id,
            'md': xmd,
            'lang': FAILBACK_SYNTAX_LANG,
            'xakepcut': paywall_tag_html,
        }
        request_headers: tp.Dict[str, str] = {  # unusued
            'content-type': 'application/x-www-form-urlencoded; charset=utf-8'
        }
        request_query_params: tp.Dict[str, str] = {
            'x': config.EXTERNAL_PARSER_TOKEN or ''
        }

        query_string = urllib.parse.urlencode(request_query_params)
        prepared_url = f'{config.EXTERNAL_PARSER_URL}?{query_string}'
        response = requests.post(
            prepared_url, data=request_payload
        )
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
                published_datetime: datetime.datetime = datetime.datetime.combine(
                    published_date, datetime.datetime.min.time()
                )
                instance.published_at = published_datetime
