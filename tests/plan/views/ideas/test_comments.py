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
@patch('plan.views.ideas.send_idea_comment_notification.delay')
def test_comments_email_sent(mock_delay, _, client, users, idea):
    url = url_(idea.id)
    response = client.post(url, {
        'text': 'foo'
    })

    _.assertEqual(response.status_code, 302)
    mock_delay.assert_called()
