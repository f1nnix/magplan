from unittest.mock import patch

import pytest
from django.urls import reverse
from dynamic_preferences.users.models import UserPreferenceModel

from main.models import User, Idea


def url_():
    return reverse('ideas_index')


@pytest.mark.django_db
def test_index(_, client, idea):
    url = url_()
    response = client.get(url)
    _.assertEqual(response.status_code, 200)


@pytest.mark.django_db
def test_create(_, user, make_user, client):
    MOCK_TITLE = 'MOCK_TITLE'

    expected_recipient: User = make_user()
    expected_recipient.is_active = True
    expected_recipient.save()

    non_recipient: User = make_user()
    non_recipient.is_active = False
    non_recipient.save()

    idea_payload = {
        'title': MOCK_TITLE,
        'description': 'bar',
        'author_type': Idea.AUTHOR_TYPE_NO
    }

    url = url_()
    response = client.post(url, idea_payload)
    _.assertEqual(response.status_code, 200)

    idea = Idea.objects.get(title=MOCK_TITLE)

    assert idea.title == MOCK_TITLE
    assert idea.editor == user


@pytest.mark.django_db
@patch('plan.views.ideas.Idea._send_vote_notification')
def test_send_vote_notifications(
        mock_send_vote_notification, make_user, make_idea,
):
    # HACK: deactivate all users, created by fixtures to clean test stand
    User.objects.update(is_active=False)

    idea_editor: User = make_user(is_active=True)
    idea: Idea = make_idea(editor=idea_editor)

    _: User = make_user(is_active=False)  # should not be sent to this user

    user_2: User = make_user(is_active=True)

    # Add user preference to get new idea notifications
    UserPreferenceModel.objects.create(
        section='plan', name='new_idea_notification', raw_value='yes',
        instance=user_2
    )

    idea.send_vote_notifications()

    assert mock_send_vote_notification.call_count == 1
    mock_send_vote_notification.assert_called_with(user_2)
