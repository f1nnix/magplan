from dynamic_preferences.preferences import Section
from dynamic_preferences.types import ChoicePreference
from dynamic_preferences.users.registries import user_preferences_registry

plan = Section('plan')


@user_preferences_registry.register
class PlanUILanguage(ChoicePreference):
    name = 'ui_language'
    section = plan
    choices = [('en', 'English'), ('ru', 'Русский')]
    default = 'ru'
