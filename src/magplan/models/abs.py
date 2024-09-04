import typing as tp

from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import QuerySet

from magplan.utils import current_site_id

class AbstractBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    _old_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class AbstractSiteModel(models.Model):
    """
    Support for multisite managers
    """

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, default=current_site_id
    )
    objects = models.Manager()
    on_current_site = CurrentSiteManager()

    class Meta:
        abstract = True

    @classmethod
    def on_site(cls, site: tp.Optional[Site]) -> QuerySet:
        if not site:
            return cls.objects

        return cls.objects.filter(site=site)
