import pytest
from django.urls import reverse


def url_():
    return reverse('ideas_index')


@pytest.mark.django_db
def test_index( _, client, idea):
    url = url_()
    response = client.get(url)

    _.assertEqual(response.status_code, 200)