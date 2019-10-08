from unittest.mock import patch

import pytest
from django.urls import reverse


def route_url(post_id: int) -> str:
    route_name = 'posts_comments'
    return reverse(route_name, kwargs={
        'post_id': post_id,
    })


@pytest.mark.django_db
@patch('plan.views.posts.send_post_comment_notification.delay')
def test_comments_notifcation_task_runs(mock_send_task_delay, _, client, post):
    url = route_url(post.id)
    response = client.post(url, {
        'text': 'foo'
    })

    _.assertEqual(response.status_code, 302)
    mock_send_task_delay.assert_called()
