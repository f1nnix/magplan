from unittest.mock import patch

import pytest

from main.models import Comment
from plan.tasks.send_idea_comment_notification import (
    _get_recipients,
    _can_receive_notification,
)


@pytest.mark.django_db
def test_no_email_permissions(idea_comment):
    recipients = _get_recipients(idea_comment)

    assert not recipients


@pytest.mark.django_db
@patch('plan.tasks.send_idea_comment_notification._can_receive_notification')
def test_editor_receives_comment(mock_can_receive_notification, idea_comment, users):
    mock_can_receive_notification.return_value = True

    recipients = _get_recipients(idea_comment)
    assert len(recipients) == 1

    recipient = next(iter(recipients))
    assert recipient == idea_comment.commentable.editor


@pytest.mark.django_db
@patch('plan.tasks.send_idea_comment_notification._can_receive_notification')
def test_previous_comments_included(mock_can_receive_notification, idea_comment, users):
    for user in users[5:]:
        Comment.objects.create(commentable=idea_comment.commentable, user=user)

    recipients = _get_recipients(idea_comment)

    # 1 for idea editor
    # 5 for prev comment authors
    assert len(recipients) == 6


@pytest.mark.django_db
def test_can_receive_notification_comment_author(idea_comment):
    assert (
        _can_receive_notification(idea_comment.commentable.editor, idea_comment)
        is False
    )


@pytest.mark.django_db
def test_can_receive_notification_user_wo_permission(idea_comment, users):
    for user in users[1:]:
        assert _can_receive_notification(user, idea_comment) is False


@pytest.mark.django_db
def test_can_receive_notification_user_with_permission(
    idea_comment, idea_email_permission, users
):
    # First user is comment author, it should
    # not receive even if has permission
    users[0].user_permissions.add(idea_email_permission)
    assert _can_receive_notification(users[0], idea_comment) is False

    for user in users[1:]:
        user.user_permissions.add(idea_email_permission)
        assert _can_receive_notification(user, idea_comment) is True
