from django.contrib.sites.models import Site
from django.db import models
from dynamic_preferences.models import PerInstancePreferenceModel


class SitePreferenceModel(PerInstancePreferenceModel):

    instance = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name="sites"
    )

    class Meta:
        # Specifying the app_label here is mandatory for backward
        # compatibility reasons, see #96
        app_label = "magplan"
