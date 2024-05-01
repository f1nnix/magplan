from dynamic_preferences.registries import PerInstancePreferenceRegistry


class SitePreferenceRegistry(PerInstancePreferenceRegistry):
    pass


site_preferences_registry = SitePreferenceRegistry()
