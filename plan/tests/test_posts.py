import datetime
from django.urls import reverse
from django.test import Client, TestCase
from main.models import Post, Comment
from plan.tests import _User, _Sections, _Section, _Stages, _Post, _Postype, _Issue
from constance import config
from django.core import mail
from django.template import Template, Context
from django.contrib.auth.models import Permission
from unittest.mock import patch

class TestSetStage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = _User()
        cls.system_user = _User()
        cls.stages = _Stages()
        cls.sections = _Sections()
        cls.postype = _Postype()
        cls.post = _Post()

        cls.new_editor = _User()
        cls.new_author = _User()
        cls.new_section = _Section()
        cls.new_issue = _Issue()

    def setUp(self):
        self.ROUTE_NAME = 'posts_set_stage'
        self.client = Client()
        self.client.force_login(user=self.user)

        config.SYSTEM_USER_ID = self.system_user.id

    def test_redirect_to_login_if_not_authenticated(self):
        client = Client()
        response = client.get(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }))
        self.assertEqual(response.status_code, 302)

    def test_redirect_to_post_for_get(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('posts_show', kwargs={
            'post_id': self.post.id,
        }))


class TestEdit(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = _User()
        cls.system_user = _User()
        cls.stages = _Stages()
        cls.sections = _Sections()
        cls.postype = _Postype()
        cls.post = _Post()

        cls.new_editor = _User()
        cls.new_author = _User()
        cls.new_section = _Section()
        # queryset filters
        cls.new_section.is_archived = False
        cls.new_section.is_whitelisted = False
        cls.new_section.save()

        cls.new_issue = _Issue()

    def setUp(self):
        self.ROUTE_NAME = 'posts_edit'
        self.client = Client()
        self.client.force_login(user=self.user)

        config.SYSTEM_USER_ID = self.system_user.id

    def test_redirect_to_login_if_not_authenticated(self):
        client = Client()
        response = client.get(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }))
        self.assertEqual(response.status_code, 302)

    def test_allow_access_to_page_if_has_auth(self):
        self.client.force_login(user=self.user)
        response = self.client.get(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }))
        self.assertEqual(response.status_code, 200)


class TestShow(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = _User()
        cls.system_user = _User()
        cls.stages = _Stages()
        cls.sections = _Sections()
        cls.postype = _Postype()
        cls.post = _Post()

    def setUp(self):
        self.ROUTE_NAME = 'posts_show'
        self.client = Client()
        self.client.force_login(user=self.user)

        self.instance_template = '<h1>{post.title}</h1>'
        config.PLAN_POSTS_INSTANCE_CHUNK = self.instance_template

    def test_show(self):
        response = self.client.get(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }))
        self.assertEqual(response.status_code, 200)

    def test_intance_template_code_should_be_rendered_from_config(self):
        intance_template = Template(config.PLAN_POSTS_INSTANCE_CHUNK)
        instance_chunk = intance_template.render(Context({
            'post': self.post,
        }))

        response = self.client.get(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, instance_chunk)

class TestComments(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = _User()
        cls.user2 = _User()
        cls.system_user = _User()
        cls.stages = _Stages()
        cls.sections = _Sections()
        cls.postype = _Postype()
        cls.post = _Post()

        cls.recieve_email_perm = Permission.objects.get(name='Recieve email updates for Post')

    def setUp(self):
        self.ROUTE_NAME = 'posts_comments'
        self.client = Client()
        self.client.force_login(user=self.user)

    @patch('plan.views.posts.EmailMultiAlternatives.send')
    def test_comment_email_not_sent_without_permission(self, mock_send):
        url = reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        })

        response = self.client.post(url, {
            'text': 'foo'   
        })
        
        self.assertEqual(response.status_code, 302)
        mock_send.assert_not_called()


    @patch('plan.views.posts.EmailMultiAlternatives.send')
    def test_comment_email_sent_with_permission(self, mock_send):
        # Allow user2 to recieve post email updates
        self.user2.user_permissions.add(self.recieve_email_perm)

        url = reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        })

        response = self.client.post(url, {
            'text': 'foo'   
        })
        self.assertEqual(response.status_code, 302)
        mock_send.assert_called()


