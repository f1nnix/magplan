import pytest
from django.urls import reverse

url = reverse('index_index')


@pytest.mark.django_db
def test_redirect_to_login_if_not_authenticated(_, anonymous_client):
    expected_url = f'{reverse("login")}?next=/admin/'

    resp = anonymous_client.get(url)
    assert resp.status_code == 302
    assert resp.url == expected_url


@pytest.mark.django_db
def test_allow_access_to_page_if_has_auth(_, client):
    with _.assertTemplateUsed('plan/index/index.html'):
        resp = client.get(url)
        assert resp.status_code == 200
