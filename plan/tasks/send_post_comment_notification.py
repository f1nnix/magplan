# Create your tasks here
from __future__ import absolute_import, unicode_literals

import logging
import os
from typing import Set

import html2text
from celery import shared_task
from constance import config
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from dynamic_preferences.users.models import UserPreferenceModel

from main.models import Comment, User

RECIEVE_NOTIFICATIONS_PERMISSION = 'main.recieve_post_email_updates'


def _can_recieve_notification(user: User, comment: Comment) -> bool:
    if config.SYSTEM_USER_ID and user.id == config.SYSTEM_USER_ID:
        return False

    if user == comment.user:
        return False

    if not user.has_perm(RECIEVE_NOTIFICATIONS_PERMISSION):
        return False

    return True


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


def _send_email(comment, recipients):
    subject = f"Комментарий к посту «{comment.commentable}» от {comment.user}"
    commentable_type = (
        "post" if comment.commentable.__class__.__name__ == "Post" else "idea"
    )
    html_content = render_to_string(
        "email/new_comment.html",
        {
            "comment": comment,
            "commentable_type": commentable_type,
            "APP_URL": os.environ.get("APP_URL", None),
        },
    )
    text_content = html2text.html2text(html_content)
    msg = EmailMultiAlternatives(
        subject, text_content, config.PLAN_EMAIL_FROM, recipients
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def _get_whitelisted_recipients() -> set:
    """Get all users, who should recieve all
    post comments notifications

    :return: Set of users, who we should send
             every comment
    """
    preferences = UserPreferenceModel.objects.filter(

    )
    return {}


def _get_blacklisted_recipients() -> set:
    """Get all users, who should NOT recieve
    any post comments notifications

    :return: Set of users, who we should not send
             any comment
    """
    ...


def _get_related_recipients(comment: Comment) -> set:
    """

    :param comment:
    :return:Ø
    """
    post = comment.commentable

    # Django objects are hashable, so we can add
    # any probabl reciever to common set, and then
    # filter by permissions
    recipients = set()

    # Add current stage assignee
    recipients.add(post.assignee)

    # Add post authors and editors
    recipients.add(post.editor)
    recipients.update([author for author in post.authors.all()])

    # Add all previous commenters in the tread
    previous_comments = Comment.objects.filter(
        content_type=ContentType.objects.get_for_model(post),
        object_id=post.id,
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
    # whitelisted = _get_whitelisted_recipients()
    # blacklisted = _get_blacklisted_recipients()
    # related = _get_related_recipients(comment)

    # Combine result sets with different
    # application rules
    # recipients = related.add(whitelisted)
    # recipients = recipients.difference(blacklisted)

    # Remove users, who cannot receive notifications
    # due to their permissions or comment ownership
    # recipients = {
    #     recipient
    #     for recipient in recipients
    #     if _can_recieve_notification(recipient, comment)
    # }

    return ()
