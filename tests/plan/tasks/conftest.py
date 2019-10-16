import pytest
from django.contrib.auth.models import Permission


@pytest.fixture
def post_email_permission():
    recieve_email_perm = Permission.objects.get(codename='recieve_post_email_updates')
    return recieve_email_perm


@pytest.fixture
def idea_email_permission():
    recieve_email_perm = Permission.objects.get(name='Recieve email updates for Idea')
    return recieve_email_perm


@pytest.fixture
def user_with_permissions(users, post_email_permission, idea_email_permission):
    user = users[-1]
    user.user_permissions.add(post_email_permission)
    user.user_permissions.add()

    yield user

    user.user_permissions.remove(post_email_permission)
    user.user_permissions.remove(idea_email_permission)


@pytest.fixture
def restricted_reciever(user_with_permissions):
    user_with_permissions.preferences['plan__post_comment_notification_level'] = 'none'

    yield user_with_permissions

    user_with_permissions.preferences[
        'plan__post_comment_notification_level'
    ] == 'related'
