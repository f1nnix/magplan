from unittest.mock import patch

import pytest

from main.models import Comment
from plan.tasks.send_post_comment_notification import (
    _get_involved_users,
    _get_recipients,
    _send_email,
    send_post_comment_notification,
)
from tests.plan.tasks.test_utils import in_


@pytest.mark.django_db
def test_get_involved_users_editor_added(comment, users):
    recipients = _get_involved_users(comment)
    assert in_(recipients, comment.commentable.editor.id, 'id')


@pytest.mark.django_db
def test_get_involved_users_authors_added(comment, users):
    recipients = _get_involved_users(comment)
    assert in_(recipients, comment.commentable.authors.all()[0].id, 'id')
    assert in_(recipients, comment.commentable.authors.all()[1].id, 'id')


@pytest.mark.django_db
def test_get_involved_users_commenters_added(comment, users):
    post = comment.commentable

    user1, user2 = users[-1:-3:-1]
    comment1 = Comment.objects.create(user=user1, commentable=post)
    comment2 = Comment.objects.create(user=user2, commentable=post)

    users = _get_involved_users(comment)
    assert in_(users, user1.id, 'id')
    assert in_(users, user2.id, 'id')


@pytest.mark.django_db
@patch('magplan.tasks.send_post_comment_notification._get_involved_users')
@patch('magplan.tasks.send_post_comment_notification._get_whitelisted_recipients')
@patch('magplan.tasks.send_post_comment_notification._can_recieve_notification')
def test_get_recipients(
    mock_can_recieve_notification, mock_get_whitelisted_recipients, mock_get_involved_users, comment
):
    mock_get_involved_users.return_value = {1, 2, 3}
    mock_get_whitelisted_recipients.return_value = {2, 3, 4}
    mock_can_recieve_notification.return_value = True

    recipients = _get_recipients(comment)
    assert recipients == {1, 2, 3, 4}


@pytest.mark.django_db
@patch('magplan.tasks.send_post_comment_notification.EmailMultiAlternatives.send')
def test_send_email(mock_send, comment):
    _send_email(comment, ())
    mock_send.assert_called()


@pytest.mark.django_db
@patch('magplan.tasks.send_post_comment_notification._get_recipients')
@patch('magplan.tasks.send_post_comment_notification._send_email')
def test_send_post_comment_notification(mock_send_email, mock_get_recipients, users, comment):
    mock_get_recipients.return_value = users[:2]

    send_post_comment_notification(comment.id)

    expected_recipients = set()
    expected_recipients.add(users[0].email)
    expected_recipients.add(users[1].email)
    mock_send_email.assert_called_with(comment, expected_recipients)
