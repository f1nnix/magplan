from random import choice
from unittest.mock import patch

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse


def route_url(post_id: int) -> str:
    route_name = 'posts_set_stage'
    return reverse(route_name, kwargs={
        'post_id': post_id,
    })


def _get_arbitrary_stage_id(post, stages):
    legit_stages = (
        post.stage.prev_stage_id,
        post.stage.next_stage_id,
    )
    new_stage_id = legit_stages[0]
    while new_stage_id in legit_stages:
        new_stage_id = choice(stages).id
    return new_stage_id


@pytest.mark.django_db
def test_redirect_to_post_for_get(_, client, post):
    url = route_url(post.id)
    expected_redirect_url = reverse('posts_show', kwargs={
        'post_id': post.id,
    })

    resp = client.get(url)
    _.assertRedirects(resp, expected_redirect_url)


@pytest.mark.django_db
@patch('magplan.views.posts._create_system_comment')
def test_allow_set_next_stage(mock_create_system_comment, _, client, user, post, stages):
    next_stage_id = post.stage.next_stage.id
    url = route_url(post.id)
    expected_redirect_url = reverse('posts_show', kwargs={
        'post_id': post.id,
    })

    post.stage.assignee = user
    post.stage.save()

    post_data = {
        'new_stage_id': next_stage_id
    }
    resp = client.post(url, post_data)

    _.assertRedirects(resp, expected_redirect_url)
    post.refresh_from_db()
    _.assertEqual(post.stage_id, next_stage_id)


@pytest.mark.django_db
@patch('magplan.views.posts._create_system_comment')
def test_allow_set_prev_stage(mock_create_system_comment, _, client, user, post, stages):
    prev_stage_id = post.stage.prev_stage_id
    url = route_url(post.id)
    expected_redirect_url = reverse('posts_show', kwargs={
        'post_id': post.id,
    })

    post.stage.assignee = user
    post.stage.save()

    post_data = {
        'new_stage_id': prev_stage_id
    }
    resp = client.post(url, post_data)

    _.assertRedirects(resp, expected_redirect_url)
    post.refresh_from_db()
    _.assertEqual(post.stage_id, prev_stage_id)


@pytest.mark.django_db
@patch('magplan.views.posts._create_system_comment')
def test_forbid_set_arbitrary_stage_wo_perm(mock_create_system_comment, _, client, post, stages):
    # Select arbitrary stage
    old_stage_id = post.stage_id
    new_stage_id = _get_arbitrary_stage_id(post, stages)

    url = route_url(post.id)

    post_data = {
        'new_stage_id': new_stage_id
    }
    resp = client.post(url, post_data)
    post.refresh_from_db()

    _.assertEqual(resp.status_code, 403)
    _.assertEqual(post.stage_id, old_stage_id)


@pytest.mark.django_db
@patch('magplan.views.posts._create_system_comment')
def test_forbid_set_arbitrary_stage_wo_perm(mock_create_system_comment, _, client, user, post, stages):
    # Select arbitrary stage
    old_stage_id = post.stage_id
    new_stage_id = _get_arbitrary_stage_id(post, stages)

    edit_extended_meta_perm = Permission.objects.get(name='Edit extended Post attributes')
    user.user_permissions.add(edit_extended_meta_perm)

    url = route_url(post.id)
    post_data = {
        'new_stage_id': new_stage_id
    }
    resp = client.post(url, post_data)
    post.refresh_from_db()

    _.assertEqual(resp.status_code, 302)
    post.refresh_from_db()
    _.assertEqual(post.stage_id, new_stage_id)
