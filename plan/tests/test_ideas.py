import datetime
from django.urls import reverse
from django.test import Client, TestCase
from main.models import Post, Comment
from plan.tests import _User, _Sections, _Section, _Stages, _Post, _Postype, _Issue, _Idea
from constance import config
from django.core import mail
from django.template import Template, Context
from django.contrib.auth.models import Permission
from unittest.mock import patch



class TestComments(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = _User()
        cls.user2 = _User()
        cls.idea = _Idea(editor=cls.user)


        cls.recieve_email_perm = Permission.objects.get(name='Recieve email updates for Idea')

    def setUp(self):
        self.ROUTE_NAME = 'ideas_comments'
        self.client = Client()
        self.client.force_login(user=self.user)

    @patch('plan.views.ideas.EmailMultiAlternatives.send')
    def test_comment_email_not_sent_without_permission(self, mock_send):
        url = reverse(self.ROUTE_NAME, kwargs={
            'idea_id': self.idea.id,
        })

        response = self.client.post(url, {
            'text': 'foo'   
        })
        
        self.assertEqual(response.status_code, 302)
        mock_send.assert_not_called()


    @patch('plan.views.ideas.EmailMultiAlternatives.send')
    def test_comment_email_sent_with_permission(self, mock_send):
        # Allow another user to recieve post email updates
        self.user2.user_permissions.add(self.recieve_email_perm)

        url = reverse(self.ROUTE_NAME, kwargs={
            'idea_id': self.idea.id,
        })

        response = self.client.post(url, {
            'text': 'foo'   
        })
        self.assertEqual(response.status_code, 302)
        mock_send.assert_called()


