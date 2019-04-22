import datetime

import django
import mistune
from authtools.models import AbstractEmailUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils import timezone

from xmd import XMDRenderer


class AbstractBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    _old_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class User(AbstractEmailUser, AbstractBase):
    meta = JSONField(default=dict)

    def __str__(self):
        p = self.profile
        if p.l_name and p.f_name:
            return '%s %s' % (p.l_name, p.f_name)
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
            ("manage_authors", "Can manage authors"),
        )


class Profile(AbstractBase):
    is_public = models.BooleanField(null=False, blank=False, default=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    f_name = models.CharField('Имя', max_length=255, blank=True, null=True)
    m_name = models.CharField('Отчество', max_length=255, blank=True, null=True)
    l_name = models.CharField('Фамилия', max_length=255, blank=True, null=True)
    n_name = models.CharField('Ник', max_length=255, blank=True, null=True)

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
    country = models.SmallIntegerField('Страна',
                                       choices=COUNTRY_CHOICES,
                                       default=RUSSIA,
                                       )
    city = models.CharField('Город или поселок', max_length=255, blank=True, null=True)
    notes = models.TextField('Примечания', blank=True, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Section(AbstractBase):
    def __str__(self):
        return self.title

    slug = models.SlugField(null=False, blank=False, max_length=255, )
    title = models.CharField(null=False, blank=False, max_length=255, )
    description = models.TextField(null=True, blank=False)
    sort = models.SmallIntegerField(null=False, blank=False, default=0)
    color = models.CharField(null=False, blank=False, default='000000', max_length=6, )
    is_archived = models.BooleanField(null=False, blank=False, default=False)
    is_whitelisted = models.BooleanField(null=False, blank=False, default=False)


class Magazine(AbstractBase):
    slug = models.SlugField(null=False, blank=False, max_length=255, )
    title = models.CharField(null=False, blank=False, max_length=255, )
    description = models.TextField(null=False, blank=True)

    def __str__(self):
        return self.title


class Issue(AbstractBase):
    class Meta:
        ordering = ['-number']

    def __str__(self):
        return '%s #%s' % (
            self.magazine,
            self.number,
        )

    number = models.SmallIntegerField(null=False, blank=False, default=0)
    title = models.CharField(null=True, blank=False, max_length=255, )
    description = models.TextField(null=True, blank=False)
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE, )
    published_at = models.DateField(null=False, blank=False, default=datetime.date.today)


class Stage(AbstractBase):
    def __str__(self):
        return self.title

    slug = models.SlugField(null=False, blank=False, max_length=255, )
    title = models.CharField(null=False, blank=False, max_length=255, )
    sort = models.SmallIntegerField(null=False, blank=False, default=0)
    duration = models.SmallIntegerField(null=True, blank=True, default=1)
    assignee = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, )
    prev_stage = models.ForeignKey('self', related_name='n_stage', null=True, blank=True, on_delete=models.CASCADE, )
    next_stage = models.ForeignKey('self', related_name='p_stage', null=True, blank=True, on_delete=models.CASCADE, )
    skip_notification = models.BooleanField(null=False, blank=False, default=False)
    meta = JSONField(default=dict)


class Idea(AbstractBase):
    title = models.CharField(null=False, blank=False, max_length=255, verbose_name='Заголовок идеи', )
    description = models.TextField(verbose_name='Описание идеи')
    approved = models.BooleanField(null=True, )
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.OneToOneField('Post', on_delete=models.SET_NULL, null=True, blank=True)
    comments = GenericRelation('Comment')

    def voted(self, user):
        vote = next((v for v in self.votes.all() if v.user_id == user.id), None)

        if vote:
            return True
        return False

    def __str__(self):
        return self.title

    class Meta:
        permissions = (
            ("approve_ideas", "Can approve ideas"),
        )

    @property
    def comments_(self):
        return self.comments.order_by('created_at').all

    @property
    def score(self):
        all_scores = sum(
            [v.score for v in self.votes.all()]
        )
        return round(all_scores / len(self.votes.all()) / 2 * 100)

    @property
    def description_html(self):
        renderer = XMDRenderer(images=[])
        markdown = mistune.Markdown(renderer=renderer)
        return markdown(self.description)


class Postype(AbstractBase):
    slug = models.SlugField(null=False, blank=False, max_length=255, )
    title = models.CharField(null=False, blank=False, max_length=255, )
    meta = JSONField(default=dict)


class Widgetype(AbstractBase):
    slug = models.SlugField(null=False, blank=False, max_length=255, )
    title = models.CharField(null=False, blank=False, max_length=255, )
    meta = JSONField(default=dict)


class Post(AbstractBase):
    def __str__(self):
        if self.kicker is None:
            return self.title

        separator = ' ' if self.kicker.endswith(('!', ':', '?')) else '. '
        return f'{self.kicker}{separator}{self.title}'

    POST_FORMAT_DEFAULT = 0
    POST_FORMAT_FEATURED = 1
    POST_FORMAT_CHOICES = (
        (POST_FORMAT_DEFAULT, 'Default'),
        (POST_FORMAT_FEATURED, 'Featured'),
    )

    format = models.SmallIntegerField(choices=POST_FORMAT_CHOICES, default=POST_FORMAT_DEFAULT)
    published_at = models.DateTimeField(null=False, blank=False, default=django.utils.timezone.now,
                                        verbose_name='Дедлайн')
    kicker = models.CharField(null=True, blank=True, max_length=255, )
    slug = models.SlugField(null=True, blank=True, max_length=255, )
    title = models.CharField(null=True, blank=True, max_length=255, verbose_name='Заголовок статьи')
    description = models.TextField(null=False, blank=True, verbose_name='Описание статьи')
    views = models.IntegerField(default=0)
    is_paywalled = models.BooleanField(default=False)
    xmd = models.TextField(null=True)
    html = models.TextField(null=True)

    editor = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="edited",
                               verbose_name='Редактор')
    authors = models.ManyToManyField(User, verbose_name='Авторы')
    postype = models.ForeignKey(Postype, on_delete=models.CASCADE, )
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, verbose_name='Этап')
    issues = models.ManyToManyField(Issue, related_name='posts', verbose_name='Выпуски')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=False, blank=False, verbose_name='Раздел')
    last_updater = models.ForeignKey(User, related_name='posts_updated', verbose_name='Кто последний обновлял',
                                     null=True, on_delete=models.SET_NULL)

    meta = JSONField(default=dict)

    comments = GenericRelation('Comment')

    def imprint_updater(self, user: User) -> None:
        """Update updated_at timestamp and set provided user as last_updater.

        `created_at` may be overwritten further on DB-hook level.
        .save() method should be explicitly called.
        """
        self.last_updater = user
        self.updated_at = datetime.datetime.now()

    @property
    def images(self):
        return list(filter(lambda a: a.type == Attachment.TYPE_IMAGE, self.attachment_set.all()))

    @property
    def pdfs(self):
        return list(filter(lambda a: a.type == Attachment.TYPE_PDF, self.attachment_set.all()))

    @property
    def files(self):
        return list(filter(lambda a: a.type == Attachment.TYPE_FILE, self.attachment_set.all()))

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
        if self.xmd is not None and self.xmd != '':
            return True
        return False

    class Meta:
        permissions = (
            ("move_post_to_any_stage", "Can move post to any stage"),
        )

    @property
    def is_overdue(self):
        if self.stage.slug in ('vault', 'published'):
            return False
        return timezone.now() > self.published_at

    @property
    def description_html(self):
        renderer = XMDRenderer(images=[])
        markdown = mistune.Markdown(renderer=renderer)
        return markdown(self.description)


class Widget(AbstractBase):
    content = models.TextField()


class Attachment(AbstractBase):
    TYPE_IMAGE = 0
    TYPE_PDF = 1
    TYPE_FILE = 2
    TYPE_CHOICES = (
        (TYPE_IMAGE, 'Image',),
        (TYPE_PDF, 'PDF',),
        (TYPE_FILE, 'File',),
    )
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_IMAGE, )

    original_filename = models.CharField(null=False, blank=False, max_length=255, )
    file = models.FileField(upload_to='attachments/%Y/%m/%d/', max_length=2048)
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, )


class Comment(AbstractBase):
    SYSTEM_ACTION_SET_STAGE = 5
    SYSTEM_ACTION_UPDATE = 10

    TYPE_SYSTEM = 5
    TYPE_PRIVATE = 10
    TYPE_PUBLIC = 15
    TYPE_CHOICES = (
        (TYPE_SYSTEM, 'system',),
        (TYPE_PRIVATE, 'private',),
        (TYPE_PUBLIC, 'public',),
    )
    text = models.TextField(blank=True)
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_PRIVATE, )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    commentable = GenericForeignKey('content_type', 'object_id', )
    meta = JSONField(default=dict)

    def __str__(self):
        return '%s, %s:%s...' % (
            self.user_id,
            self.type,
            self.text[0:50],
        )

    @property
    def html(self):
        renderer = XMDRenderer(images=[])
        markdown = mistune.Markdown(renderer=renderer)
        return markdown(self.text)


class Vote(AbstractBase):
    SCORE_NEGATIVE = 0
    SCORE_NEUTRAL = 1
    SCORE_POSITIVE = 2
    SCORE_CHOICES = (
        (SCORE_NEGATIVE, 'Не стану читать даже даром',),
        (SCORE_NEUTRAL, 'Прочел бы, встретив в журнале',),
        (SCORE_POSITIVE, 'Ради таких статей готов купить журнал',),
    )
    score = models.SmallIntegerField(choices=SCORE_CHOICES, default=SCORE_NEUTRAL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name='votes')

    @property
    def score_humanized(self):
        return self.__class__.SCORE_CHOICES


@receiver(pre_save, sender=Post)
def render_xmd(sender, instance, **kwargs):
    if instance.has_text:
        renderer = XMDRenderer(images=instance.images)
        markdown = mistune.Markdown(renderer=renderer)
        instance.html = markdown(instance.xmd)
