from django.test import Client, TestCase
from django.urls import reverse
from plan.tests import _User


class TestIndex(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = _User()

    def setUp(self):
        self.ROUTE_NAME = 'index_index'
        self.client = Client()

    def test_redirect_to_login_if_not_authenticated(self):
        response = self.client.get(reverse(self.ROUTE_NAME))
        self.assertRedirects(response, f'{reverse("login")}?next=/admin/')

    def test_allow_access_to_page_if_has_auth(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(self.ROUTE_NAME))
        self.assertEqual(response.status_code, 200)


