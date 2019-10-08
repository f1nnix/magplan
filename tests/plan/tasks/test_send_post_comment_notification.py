import pytest

from typing import List, Any
from unittest.mock import patch
from main.models import Comment
from plan.tasks.send_post_comment_notification import (
    _get_involved_users,
    _get_whitelisted_recipients,
    _can_recieve_notification,
    _get_recipients,
)


def in_(arr: List[Any], value: Any, key: str) -> bool:
    """Check, if object with requested attrubute value
    exists in list

    :param arr: List to search elements in
    :param value: Value to search
    :param key: Key to search value of
    :return: True is exists, else False.
    """
    try:
        search_results = [True for obj in arr if getattr(obj, key) == value]
    except KeyError:
        raise KeyError('Key "%s" does not exist in list element(s)' % key)
    return bool(search_results)


@pytest.mark.django_db
def test_get_involved_users_post_staff_added(comment, users):
    post = comment.commentable
    post_authors = post.authors.all()
    users = _get_involved_users(comment)

    assert in_(users, post.assignee.id, 'id') == True
    assert in_(users, post.editor.id, 'id') == True
    assert in_(users, post_authors[0].id, 'id') == True
    assert in_(users, post_authors[1].id, 'id') == True


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
def test_get_whitelisted_recipients(users):
    user1, user2, user3 = users[-1:-4:-1]
    for user in (user1, user2, user3):
        user.preferences['plan__post_comment_notification_level'] = 'all'

    whitelisted_recipients = _get_whitelisted_recipients()
    assert len(whitelisted_recipients) == 3
    assert in_(whitelisted_recipients, user1.id, 'id')
    assert in_(whitelisted_recipients, user2.id, 'id')
    assert in_(whitelisted_recipients, user3.id, 'id')


@pytest.mark.django_db
def test_can_recieve_notification_no_permission(comment, users):
    assert _can_recieve_notification(users[-1], comment) == False


@pytest.mark.django_db
def test_can_recieve_notification_with_permission(user_with_permissions, comment):
    assert _can_recieve_notification(user_with_permissions, comment) == True


@pytest.mark.django_db
def test_can_recieve_notification_comment_owner(comment, user_with_permissions):
    assert _can_recieve_notification(user_with_permissions, comment) == True

    comment.user = user_with_permissions
    comment.save()
    assert _can_recieve_notification(user_with_permissions, comment) == False


@pytest.mark.django_db
@patch('plan.tasks.send_post_comment_notification.config')
def test_can_recieve_notification_system_user(config, comment, user_with_permissions):
    config.SYSTEM_USER_ID = user_with_permissions.id

    assert _can_recieve_notification(user_with_permissions, comment) == False


@pytest.mark.django_db
def test_can_recieve_notification_user_settings(comment, restricted_reciever):
    assert _can_recieve_notification(restricted_reciever, comment) == False


@pytest.mark.django_db
@patch('plan.tasks.send_post_comment_notification._get_involved_users')
@patch('plan.tasks.send_post_comment_notification._get_whitelisted_recipients')
@patch('plan.tasks.send_post_comment_notification._can_recieve_notification')
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
