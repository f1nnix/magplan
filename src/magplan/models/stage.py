from django.db import models
from django.db.models import JSONField

from magplan.models.abs import AbstractSiteModel, AbstractBase
from magplan.models.user import User


class Stage(AbstractSiteModel, AbstractBase):
    def __str__(self):
        return self.title

    slug = models.SlugField(null=False, blank=False, max_length=255)
    title = models.CharField(null=False, blank=False, max_length=255)
    sort = models.SmallIntegerField(null=False, blank=False, default=0)
    duration = models.SmallIntegerField(null=True, blank=True, default=1)
    assignee = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE
    )
    prev_stage = models.ForeignKey(
        "self",
        related_name="n_stage",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    next_stage = models.ForeignKey(
        "self",
        related_name="p_stage",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    skip_notification = models.BooleanField(
        null=False, blank=False, default=False
    )
    meta = JSONField(default=dict)
