import pytest
from django.test import Client


@pytest.fixture
def client(user):
    test_client = Client()
    test_client.force_login(user=user)
    yield test_client


@pytest.fixture
def anonymous_client():
    test_client = Client()
    yield test_client
