# Create your tasks here
from __future__ import absolute_import, unicode_literals

import logging
import os
from typing import Set

import html2text
from magplan.conf import settings as config
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from celery import shared_task
from magplan.models import Comment, User
from magplan.tasks.utils import _can_recieve_notification, _get_whitelisted_recipients

RECIEVE_NOTIFICATIONS_PERMISSION = 'main.recieve_idea_email_updates'
NOTIFICATION_LEVEL_PREFERENCE = 'idea_comment_notification_level'


def _get_involved_users(comment: Comment) -> set:
    """

    :param comment:
    :return: Ø
    """
    idea = comment.commentable

    # Django objects are hashable, so we can add
    # any probable receiver to common set, and then
    # filter by permissions
    recipients = set()

    # Add current stage assignee
    recipients.add(idea.editor)

    # Add all previous comments in the tread
    previous_comments = Comment.objects.filter(
        content_type=ContentType.objects.get_for_model(idea),
        object_id=idea.id,
        # Not required, as idea comments are always private
        type=Comment.TYPE_PRIVATE,
    ).exclude(id=comment.id)
    recipients.update([pc.user for pc in previous_comments])

    return recipients


def _get_recipients(comment: Comment) -> Set[User]:
    """Build final list of notification recipients
    for comments.

    Includes:

    — those, who should receive all notifications;
    — those, who comment is related to.

    Excludes users, who restricted any post comments
    notifications.

    :param comment: Comment, for which we build
                    recipient list for
    :return: Final set of actual recipients
    """
    recipients = set()

    involved_users = _get_involved_users(comment)
    recipients.update(involved_users)

    whitelisted_recipients = _get_whitelisted_recipients(NOTIFICATION_LEVEL_PREFERENCE)
    recipients.update(whitelisted_recipients)

    # Remove users, who cannot receive notifications
    # due to their permissions, comment ownership or settings
    recipients = {
        recipient
        for recipient in recipients
        if _can_recieve_notification(
            recipient, comment, RECIEVE_NOTIFICATIONS_PERMISSION, NOTIFICATION_LEVEL_PREFERENCE
        )
    }

    return recipients


def _send_email(comment, recipients):
    subject = f"Комментарий к идее «{comment.commentable}» от {comment.user}"
    html_content = render_to_string(
        "email/new_comment.html",
        {"comment": comment, "commentable_type": 'idea', "APP_URL": os.environ.get('APP_URL', None)},
    )
    text_content = html2text.html2text(html_content)
    msg = EmailMultiAlternatives(subject, text_content, config.PLAN_EMAIL_FROM, recipients)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task
def send_idea_comment_notification(comment_id: int) -> None:
    """Send email notification for idea comment

    Notification is sent to:

    - idea author (user)
    - everyone, who previously commented comment idea

    But only, if users have appropriate permission
    permission and not comment author.
    """
    logger = logging.getLogger()
    logger.info('Sending notifications for comment #%s', comment_id)

    # Task will fail if comment is not found
    comment = Comment.objects.get(id=comment_id)

    recipients = _get_recipients(comment)
    if not recipients:
        return

    # Transform to plain email list
    recipients_emails = {recipient.email for recipient in recipients}

    _send_email(comment, recipients_emails)
