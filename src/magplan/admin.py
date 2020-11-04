# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter

from magplan.models import User, Post, Comment, Issue, Stage, Magazine, Section, Idea, Attachment


class UserAdmin(BaseUserAdmin):
    ordering = ['profile__l_name']

    list_display = ['profile__l_name', 'profile__f_name', 'email', ]

    def profile__f_name(self, obj):
        return obj.profile.f_name

    profile__f_name.short_description = 'First name'
    profile__f_name.admin_order_field = 'profile__f_name'

    def profile__l_name(self, obj):
        return obj.profile.l_name

    profile__l_name.admin_order_field = 'profile__l_name'
    profile__l_name.short_description = 'Last name'

    list_filter = (
        'groups__name', 'is_staff', 'is_superuser', 'is_active',
    )


class PostAdmin(admin.ModelAdmin):
    ordering = ['-created_at']

    list_filter = (
        ('stage', RelatedDropdownFilter),
        ('editor', RelatedDropdownFilter),
    )

    list_display = ('title', 'created_at', 'stage', 'section', 'editor')


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['type', 'file', 'user', 'post']
    list_filter = ['type']


class IdeaAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    list_filter = ['type']


class StageAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration', 'sort', 'skip_notification', ]


class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'sort', 'is_archived', 'is_whitelisted', ]
    list_filter = ['is_archived', 'is_whitelisted', ]


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Issue)
admin.site.register(Stage, StageAdmin)
admin.site.register(Magazine)
admin.site.register(Section, SectionAdmin)
admin.site.register(Idea, IdeaAdmin)
admin.site.register(Attachment, AttachmentAdmin)
