from django.contrib import admin
from authtools.admin import UserAdmin as AuthtoolsUserAdmin
from main.models import User, Post, Comment, Idea, Attachment, Issue, Stage, Magazine, Section
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter


class UserAdmin(AuthtoolsUserAdmin):
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
    )

    def admin_post_display_name(self, obj):
        editor = obj.editor
        return '{0} {1}, {2}, {3}'.format(
            editor.meta['l_name'],
            editor.meta['f_name'],
            '',
            '',
        )

    admin_post_display_name.short_description = 'Редактор'

    list_display = ('title', 'created_at', 'stage', 'section', 'admin_post_display_name')


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['type', 'file', 'user', 'post']
    list_filter = ['type']


class IdeaAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    list_filter = ['type']


class StageAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration', 'sort', 'skip_notification', ]


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Issue)
admin.site.register(Stage, StageAdmin)
admin.site.register(Magazine)
admin.site.register(Section)
admin.site.register(Idea, IdeaAdmin)
admin.site.register(Attachment, AttachmentAdmin)