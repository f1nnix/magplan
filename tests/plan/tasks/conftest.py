import pytest
from django.contrib.auth.models import Permission


@pytest.fixture
def post_email_permission():
    recieve_email_perm = Permission.objects.get(name='Recieve email updates for Post')
    return recieve_email_perm
