from unittest.mock import patch

# from plan.tests import _User, _Sections, _Section, _Stages, _Post, _Postype, _Issue, _Idea
import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse


def url_(idea_id):
    return reverse('ideas_comments', kwargs={
        'idea_id': idea_id,
    })


@pytest.mark.django_db
@patch('plan.views.ideas.EmailMultiAlternatives.send')
def test_comment_email_not_sent_without_permission(mock_send, _, client, idea):
    url = url_(idea.id)
    response = client.post(url, {
        'text': 'foo'
    })

    _.assertEqual(response.status_code, 302)
    mock_send.assert_not_called()


@pytest.mark.django_db
@patch('plan.views.ideas.EmailMultiAlternatives.send')
def test_comment_email_sent_with_permission(mock_send, _, client, users, idea):
    # Allow another user to recieve post email updates
    recieve_email_perm = Permission.objects.get(name='Recieve email updates for Idea')
    users[1].user_permissions.add(recieve_email_perm)

    url = url_(idea.id)
    response = client.post(url, {
        'text': 'foo'
    })

    _.assertEqual(response.status_code, 302)
    mock_send.assert_called()
