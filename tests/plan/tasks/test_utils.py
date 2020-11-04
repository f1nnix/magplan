from typing import List, Any, Optional
from unittest.mock import patch

import pytest

from plan.tasks.utils import _get_whitelisted_recipients, _can_recieve_notification

pref_name = 'post_comment_notification_level'
perm_name = 'main.recieve_post_email_updates'


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


def get_(arr: List[Any], value: Any, key: str) -> Optional[Any]:
    """Get object with requested attrubute value
    from list

    :param arr: List to search elements in
    :param value: Value to search
    :param key: Key to search value of
    :return: First object if exists, else None
    """
    try:
        search_results = [obj for obj in arr if obj[key] == value]
    except KeyError:
        raise KeyError('Key "%s" does not exist in list element(s)' % key)

    if search_results:
        return list(search_results)[0]

    return None


@pytest.mark.django_db
def test_get_whitelisted_recipients(users):
    user1, user2, user3 = users[-1:-4:-1]
    for user in (user1, user2, user3):
        user.preferences['plan__' + pref_name] = 'all'

    whitelisted_recipients = _get_whitelisted_recipients(pref_name)
    assert len(whitelisted_recipients) == 3
    assert in_(whitelisted_recipients, user1.id, 'id')
    assert in_(whitelisted_recipients, user2.id, 'id')
    assert in_(whitelisted_recipients, user3.id, 'id')


@pytest.mark.django_db
def test_can_recieve_notification_no_permission(comment, users):
    assert _can_recieve_notification(users[-1], comment, perm_name, pref_name) == False


@pytest.mark.django_db
def test_can_recieve_notification_with_permission(user_with_permissions, comment):
    assert _can_recieve_notification(user_with_permissions, comment, perm_name, pref_name)


@pytest.mark.django_db
def test_can_recieve_notification_comment_owner(comment, user_with_permissions):
    assert _can_recieve_notification(user_with_permissions, comment, perm_name, pref_name)

    comment.user = user_with_permissions
    comment.save()
    assert not _can_recieve_notification(user_with_permissions, comment, perm_name, pref_name)


@pytest.mark.django_db
@patch('magplan.tasks.utils.config')
def test_can_recieve_notification_system_user(config, comment, user_with_permissions):
    config.SYSTEM_USER_ID = user_with_permissions.id

    assert not _can_recieve_notification(user_with_permissions, comment, perm_name, pref_name)


@pytest.mark.django_db
def test_can_recieve_notification_user_settings(comment, restricted_reciever):
    assert not _can_recieve_notification(restricted_reciever, comment, perm_name, pref_name)
