from unittest.mock import patch, Mock, MagicMock

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse


def route_url(post_id: int) -> str:
    route_name = 'posts_comments'
    return reverse(route_name, kwargs={
        'post_id': post_id,
    })


@pytest.mark.django_db
@patch('plan.views.posts.EmailMultiAlternatives.send')
def test_comments_not_send_wo_permission(mock_send, _, client, post):
    url = route_url(post.id)
    response = client.post(url, {
        'text': 'foo'
    })

    _.assertEqual(response.status_code, 302)
    mock_send.assert_not_called()


@pytest.mark.django_db
@patch('plan.views.posts.EmailMultiAlternatives.send')
@patch('plan.views.posts.send_post_comment_notification')
def test_comment_email_sent_with_permission(mock_send_task, _, client, users, post):
    mock_send_task.delay = MagicMock()

    recieve_email_perm = Permission.objects.get(name='Recieve email updates for Post')
    users[1].user_permissions.add(recieve_email_perm)

    url = route_url(post.id)
    response = client.post(url, {
        'text': 'foo'
    })

    assert response.status_code == 302
    mock_send_task.delay.assert_called()
