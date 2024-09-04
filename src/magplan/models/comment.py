from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import JSONField

from magplan.models.abs import AbstractBase
from magplan.models.user import User
from magplan.xmd import render_md


class Comment(AbstractBase):
    SYSTEM_ACTION_SET_STAGE = 5
    SYSTEM_ACTION_UPDATE = 10
    SYSTEM_ACTION_CHANGE_META = 15
    SYSTEM_ACTION_CHOICES = (
        (SYSTEM_ACTION_SET_STAGE, "Set stage"),
        (SYSTEM_ACTION_UPDATE, "Update"),
        (SYSTEM_ACTION_CHANGE_META, "Change meta"),
    )

    TYPE_SYSTEM = 5
    TYPE_PRIVATE = 10
    TYPE_PUBLIC = 15
    TYPE_CHOICES = (
        (TYPE_SYSTEM, "system"),
        (TYPE_PRIVATE, "private"),
        (TYPE_PUBLIC, "public"),
    )
    text = models.TextField(blank=True)
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_PRIVATE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    commentable = GenericForeignKey("content_type", "object_id")
    meta = JSONField(default=dict)

    def __str__(self):
        return "%s, %s:%s..." % (self.user_id, self.type, self.text[0:50])

    @property
    def html(self):
        return render_md(self.text, render_lead=False)

    @property
    def changelog(self):
        try:
            md = "\n".join(self.meta["comment"]["changelog"])
        except Exception:
            md = ""

        return render_md(md, render_lead=False)
