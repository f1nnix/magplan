from django import forms
from dynamic_preferences.preferences import Section
from dynamic_preferences.types import ChoicePreference
from dynamic_preferences.users.registries import user_preferences_registry

plan = Section('plan')


@user_preferences_registry.register
class PlanUILanguage(ChoicePreference):
    name = 'ui_language'
    section = plan
    choices = [
        ('en', 'English'),
        ('ru', 'Русский')
    ]
    default = 'ru'
    widget = forms.Select(attrs={'class': 'form-control'})
    verbose_name = 'Язык интерфейса плана'


@user_preferences_registry.register
class PostCommentNotificationLevel(ChoicePreference):
    name = 'post_comment_notification_level'
    section = plan
    choices = [
        ('none', 'Не присылать уведомлений о комментариях'),
        ('related', 'Присылать только те, что относятся ко мне'),
        ('all', 'Присылать все уведомления'),
    ]
    default = 'related'
    widget = forms.Select(attrs={'class': 'form-control'})
    verbose_name = 'Уведомления о комментариях к посту'


@user_preferences_registry.register
class IdeaCommentNotificationLevel(ChoicePreference):
    name = 'idea_comment_notification_level'
    section = plan
    choices = [
        ('none', 'Не присылать уведомлений о комментариях'),
        ('related', 'Присылать только те, что относятся ко мне'),
        ('all', 'Присылать все уведомления'),
    ]
    default = 'related'
    widget = forms.Select(attrs={'class': 'form-control'})
    verbose_name = 'Уведомления о комментариях к идее'

@user_preferences_registry.register
class XMDEditorType(ChoicePreference):
    name = 'xmd_editor_type'
    section = plan
    choices = [
        ('plain', 'Plain-text редактор'),
        ('markdown', 'Markdown-редактор'),
    ]
    default = 'markdown'
    widget = forms.Select(attrs={'class': 'form-control'})
    verbose_name = 'Редактор для статей в XMD'

@user_preferences_registry.register
class NewIdeaNotificationType(ChoicePreference):
    name = 'new_editor_notification_type'
    section = plan
    choices = [
        ('yes', 'Да'),
        ('no', 'Нет'),
    ]
    default = 'yes'
    widget = forms.Select(attrs={'class': 'form-control'})
    verbose_name = 'Присылать уведомелния о новых идеях?'
