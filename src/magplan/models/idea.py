import os
import typing as tp

import html2text
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string

from magplan.conf import settings as config
from magplan.models.abc import AbstractSiteModel, AbstractBase
from magplan.models.user import User
from magplan.xmd import render_md

NEW_IDEA_NOTIFICATION_PREFERENCE_NAME = "magplan__new_idea_notification"


class Idea(AbstractSiteModel, AbstractBase):
    AUTHOR_TYPE_NO = "NO"
    AUTHOR_TYPE_NEW = "NW"
    AUTHOR_TYPE_EXISTING = "EX"
    AUTHOR_TYPE_CHOICES = [
        (AUTHOR_TYPE_NO, "Нет автора"),
        (AUTHOR_TYPE_NEW, "Новый автор"),
        (AUTHOR_TYPE_EXISTING, "Существующий автор(ы)"),
    ]
    title = models.CharField(
        null=False, blank=False, max_length=255, verbose_name="Заголовок"
    )
    description = models.TextField(verbose_name="Описание")
    approved = models.BooleanField(null=True)
    editor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="editor"
    )
    post = models.OneToOneField(
        "Post", on_delete=models.SET_NULL, null=True, blank=True
    )
    comments = GenericRelation("Comment")
    author_type = models.CharField(
        max_length=2,
        choices=AUTHOR_TYPE_CHOICES,
        default=AUTHOR_TYPE_NO,
        verbose_name="Автор",
    )
    authors_new = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Новые автор"
    )
    authors = models.ManyToManyField(
        User, verbose_name="Авторы", related_name="authors", blank=True
    )

    def voted(self, user):
        vote = next((v for v in self.votes.all() if v.user_id == user.id), None)

        if vote:
            return True
        return False

    def _send_vote_notification(self, recipient: User) -> None:
        subject = f"Новая идея «{self.title}». Голосуйте!"

        context = {"idea": self, "APP_URL": os.environ.get("APP_URL")}
        message_html_content: str = render_to_string(
            "email/new_idea.html", context
        )
        message_text_content: str = html2text.html2text(message_html_content)

        msg = EmailMultiAlternatives(
            subject,
            message_text_content,
            config.PLAN_EMAIL_FROM,
            [recipient.email],
        )
        msg.attach_alternative(message_html_content, "text/html")
        msg.send()

    def send_vote_notifications(self) -> None:
        active_users: tp.List[User] = User.objects.filter(
            is_active=True
        ).exclude(id=self.editor_id)
        recipients: tp.List[User] = [
            user
            for user in active_users
            if user.preferences[NEW_IDEA_NOTIFICATION_PREFERENCE_NAME]
        ]

        for recipient in recipients:
            self._send_vote_notification(recipient)

    def __str__(self):
        return self.title

    class Meta:
        permissions = (
            ("edit_extended_idea_attrs", "Edit extended Idea attributes"),
            ("recieve_idea_email_updates", "Recieve email updates for Idea"),
        )

    @property
    def comments_(self):
        return self.comments.order_by("created_at").all

    @property
    def score(self):
        MAX_SCORE = 100

        all_scores = sum([v.score for v in self.votes.all()])
        max_scores = len(self.votes.all()) * MAX_SCORE

        return round(all_scores / max_scores * 100)

    @property
    def description_html(self):
        return render_md(self.description)
