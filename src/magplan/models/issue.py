import datetime

from django.db import models

from magplan.models.abs import AbstractSiteModel, AbstractBase
from magplan.models.magazine import Magazine


class Issue(AbstractSiteModel, AbstractBase):
    class Meta:
        ordering = ["-number"]

    def __str__(self):
        return "%s #%s" % (self.magazine, self.number)

    number = models.SmallIntegerField(null=False, blank=False, default=0)
    title = models.CharField(null=True, blank=False, max_length=255)
    description = models.TextField(null=True, blank=False)
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE)
    published_at = models.DateField(
        null=False, blank=False, default=datetime.date.today
    )

    @property
    def full_title(self) -> str:
        return "{} #{} {}".format("Хакер", self.number, self.title or "")
