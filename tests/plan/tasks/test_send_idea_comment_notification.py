from unittest.mock import patch

import pytest

from main.models import Comment
from plan.tasks.send_idea_comment_notification import (
    _get_involved_users,
    _get_recipients,
)


@pytest.mark.django_db
def test_get_involved_users_editor_added(idea_comment, users):
    recipients = _get_involved_users(idea_comment)
    assert len(recipients) == 1

    recipient = next(iter(recipients))
    assert recipient == idea_comment.commentable.editor


@pytest.mark.django_db
def test_get_involved_users_previous_comments_added(idea_comment, users):
    for user in users[5:]:
        Comment.objects.create(commentable=idea_comment.commentable, user=user)

    recipients = _get_involved_users(idea_comment)

    # 1 for idea editor
    # 5 for prev comment authors
    assert len(recipients) == 6


@pytest.mark.django_db
@patch('plan.tasks.send_idea_comment_notification._get_involved_users')
@patch('plan.tasks.send_idea_comment_notification._get_whitelisted_recipients')
@patch('plan.tasks.send_idea_comment_notification._can_recieve_notification')
def test_get_recipients(
    mock_can_recieve_notification,
    mock_get_whitelisted_recipients,
    mock_get_involved_users,
    comment,
):
    mock_get_involved_users.return_value = {1, 2, 3}
    mock_get_whitelisted_recipients.return_value = {2, 3, 4}
    mock_can_recieve_notification.return_value = True

    recipients = _get_recipients(comment)
    assert recipients == {1, 2, 3, 4}
