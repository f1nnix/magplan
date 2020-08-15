from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from django.urls import reverse

from main.models import User, Idea, Vote


def url_():
    return reverse('ideas_index')


@pytest.mark.django_db
def test_vote_non_auth(_, anonymous_client, make_user, make_idea, ):
    idea_editor: User = make_user(is_active=True)
    idea: Idea = make_idea(editor=idea_editor)

    url_kwargs = {
        'idea_id': idea.id
    }
    url = reverse('ideas_vote', kwargs=url_kwargs)

    payload = {
        'score': 2
    }
    response = anonymous_client.post(url, payload)
    _.assertEqual(response.status_code, 302)

    # Can't simply get user here
    assert not Vote.objects.filter(score=2).exists()


@pytest.mark.django_db
def test_vote_get(_, client, make_user, make_idea):
    idea_editor: User = make_user(is_active=True)
    idea: Idea = make_idea(editor=idea_editor)

    url_kwargs = {
        'idea_id': idea.id
    }
    base_url = reverse('ideas_vote', kwargs=url_kwargs)
    query_params = urlencode(
        {
            'score': 25
        },
        doseq=True
    )
    url = f'{base_url}?{query_params}'

    response = client.get(url)
    _.assertEqual(response.status_code, 302)

    # Can't simply get user here
    assert Vote.objects.filter(score=25).exists()


@pytest.mark.django_db
def test_vote_post(_, client, make_user, make_idea, ):
    idea_editor: User = make_user(is_active=True)
    idea: Idea = make_idea(editor=idea_editor)

    url_kwargs = {
        'idea_id': idea.id
    }
    url = reverse('ideas_vote', kwargs=url_kwargs)

    payload = {
        'score': 100
    }

    response = client.post(url, payload)
    _.assertEqual(response.status_code, 302)

    # Can't simply get user here
    assert Vote.objects.filter(score=100).exists()

@pytest.mark.django_db
def test_invalid_vote_post(_, client, make_user, make_idea, ):
    idea_editor: User = make_user(is_active=True)
    idea: Idea = make_idea(editor=idea_editor)

    url_kwargs = {
        'idea_id': idea.id
    }
    url = reverse('ideas_vote', kwargs=url_kwargs)

    payload = {
        'score': 2
    }
    response = client.post(url, payload)
    _.assertEqual(response.status_code, 302)

    # Can't simply get user here
    assert Vote.objects.filter(score=50).exists()
