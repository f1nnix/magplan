import pytest
from django.urls import reverse


def route_url(post_id: int) -> str:
    route_name = 'posts_edit'
    return reverse(route_name, kwargs={
        'post_id': post_id,
    })


@pytest.mark.django_db
def test_not_authenticated(anonymous_client, post):
    url = route_url(post.id)
    resp = anonymous_client.get(url)
    assert resp.status_code == 302


@pytest.mark.django_db
def test_edit(_, client, post):
    url = route_url(post.id)

    with _.assertTemplateUsed('magplan/posts/edit.html'):
        resp = client.get(url)
        assert resp.status_code == 200
