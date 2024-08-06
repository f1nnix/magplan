from django.apps import AppConfig
from dynamic_preferences.registries import preference_models

from magplan.registries import site_preferences_registry


class PlanConfig(AppConfig):
    name = "magplan"

    def ready(self):
        SitePreferenceModel = self.get_model("SitePreferenceModel")

        preference_models.register(
            SitePreferenceModel, site_preferences_registry
        )
