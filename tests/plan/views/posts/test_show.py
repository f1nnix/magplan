from unittest.mock import patch

import pytest
from django.urls import reverse


def route_url(post_id: int) -> str:
    route_name = 'posts_show'
    return reverse(route_name, kwargs={
        'post_id': post_id,
    })


@pytest.mark.django_db
def test_not_authenticated(anonymous_client, post):
    url = route_url(post.id)
    resp = anonymous_client.get(url)
    assert resp.status_code == 302


@pytest.mark.django_db
def test_show(_, client, post):
    url = route_url(post.id)

    with _.assertTemplateUsed('plan/posts/show.html'):
        resp = client.get(url)
        assert resp.status_code == 200


@pytest.mark.django_db
@patch('plan.views.posts._get_arbitrary_chunk')
def test_instance_template_code_rendered(mock_get_arbitrary_chunk, _, client, post):
    arbitrary_chunk = 'instance-chunk'
    mock_get_arbitrary_chunk.return_value = arbitrary_chunk

    url = route_url(post.id)

    resp = client.get(url)
    assert resp.status_code == 200
    _.assertContains(resp, arbitrary_chunk)
