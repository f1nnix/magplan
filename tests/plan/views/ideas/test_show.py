import pytest
from django.urls import reverse


def url_(idea_id):
    return reverse('ideas_show', kwargs={
        'idea_id': idea_id
    })


@pytest.mark.django_db
def test_show(_, client, idea, issue):
    url = url_(idea.id)
    response = client.get(url)

    _.assertEqual(response.status_code, 200)
