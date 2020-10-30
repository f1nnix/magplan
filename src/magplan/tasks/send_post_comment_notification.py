# Create your tasks here
from __future__ import absolute_import, unicode_literals

import logging
import os
from typing import Set

import html2text
from celery import shared_task
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from magplan.conf import settings as config
from magplan.models import Comment
from magplan.tasks.utils import _can_recieve_notification, _get_whitelisted_recipients

RECIEVE_NOTIFICATIONS_PERMISSION = 'main.recieve_post_email_updates'
NOTIFICATION_LEVEL_PREFERENCE = 'post_comment_notification_level'


def _get_involved_users(comment: Comment) -> set:
    """Return all users, who involved in working
    on current post

    :param comment: Comment for post, for which we count involved users
    :return: Users set
    """
    post = comment.commentable

    # Django objects are hashable, so we can add
    # any probabl reciever to common set, and then
    # filter by permissions
    users = set()

    # Add current stage assignee
    users.add(post.assignee)

    # Add post authors and editors
    users.add(post.editor)
    users.update([author for author in post.authors.all()])

    # Add all previous commenters in the tread
    previous_comments = Comment.objects.filter(
        content_type=ContentType.objects.get_for_model(post), object_id=post.id, type=Comment.TYPE_PRIVATE
    ).exclude(id=comment.id)

    users.update([pc.user for pc in previous_comments])

    return users


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
    subject = f"Комментарий к посту «{comment.commentable}» от {comment.user}"
    commentable_type = "post" if comment.commentable.__class__.__name__ == "Post" else "idea"
    html_content = render_to_string(
        "email/new_comment.html",
        {"comment": comment, "commentable_type": commentable_type, "APP_URL": os.environ.get("APP_URL", None)},
    )
    text_content = html2text.html2text(html_content)
    msg = EmailMultiAlternatives(subject, text_content, config.PLAN_EMAIL_FROM, recipients)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def send_post_comment_notification(comment_id: int) -> None:
    """Send email notification for post comment

    Notification is sent to:

    - comment post current stage assignee
    - comment post authors and editor
    - everyone, who previously commented comment post

    But only, if users have recieve_post_email_updates
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
