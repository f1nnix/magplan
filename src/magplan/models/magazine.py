from django.db import models

from magplan.models.abs import AbstractBase


class Magazine(AbstractBase):
    slug = models.SlugField(null=False, blank=False, max_length=255)
    title = models.CharField(null=False, blank=False, max_length=255)
    description = models.TextField(null=False, blank=True)

    def __str__(self):
        return self.title
