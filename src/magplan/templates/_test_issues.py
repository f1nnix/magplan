from django.test import Client, TestCase
from plan.tests import _User, _Sections, _Section, _Stages, _Post, _Postype, _Issue
from django.urls import reverse
from datetime import datetime
from main.models import Issue


class TestCreate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = _User()

    def setUp(self):
        self.ROUTE_NAME = 'issues_create'
        self.client = Client()

    def test_redirect_to_login_if_not_authenticated(self):
        response = self.client.get(reverse(self.ROUTE_NAME))
        self.assertRedirects(response, '%s?next=/admin/issues/new/' % reverse('login'))

    def test_should_render_issue_form(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(self.ROUTE_NAME))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'magplan/issues/_form.html')

    def test_issue_should_be_created(self):
        self.client.force_login(user=self.user)

        published_at = datetime.now()
        response = self.client.post(reverse(self.ROUTE_NAME), {
            'title': 'title',
            'description': 'description',
            'number': '123',
            'published_at': published_at.strftime('%d.%m.%Y'),
        })

        self.assertRedirects(response, reverse('issues_index'))
        self.assertEqual(Issue.objects.filter(number=123), 1)
