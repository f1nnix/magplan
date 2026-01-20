from django.db import models

from magplan.models.abs import AbstractSiteModel, AbstractBase


class Section(AbstractSiteModel, AbstractBase):
    def __str__(self):
        return self.title

    slug = models.SlugField(null=False, blank=False, max_length=255)
    title = models.CharField(null=False, blank=False, max_length=255)
    description = models.TextField(null=True, blank=False)
    sort = models.SmallIntegerField(null=False, blank=False, default=0)
    color = models.CharField(
        null=False, blank=False, default="000000", max_length=6
    )
    is_archived = models.BooleanField(null=False, blank=False, default=False)
    is_whitelisted = models.BooleanField(null=False, blank=False, default=False)
