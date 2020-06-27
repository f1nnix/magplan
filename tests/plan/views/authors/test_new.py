import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse

from main.models import User

AUTHOR_EMAIL = 'foo@bar.example'
AUTHOR_FEATURES = ('l_name', 'f_name', 'n_name', 'notes')
AUTHOR_FEATURE_MOCK = 'AUTHOR_FEATURE_MOCK'


@pytest.mark.django_db
def test_new_author(_, client, user):
    manage_author_permission = Permission.objects.get(codename='manage_authors')
    user.user_permissions.add(manage_author_permission)

    author_paylod = {
        'email': AUTHOR_EMAIL,
        **{k: AUTHOR_FEATURE_MOCK for k in AUTHOR_FEATURES}
    }

    url = reverse('authors_new')
    response = client.post(url, author_paylod)

    created_author = User.objects.get(email=AUTHOR_EMAIL)
    assert not created_author.is_active

    expected_url = reverse('authors_edit', args=[created_author.id])
    _.assertRedirects(response, expected_url)
