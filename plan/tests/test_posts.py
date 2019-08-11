from random import choice
from unittest.mock import patch

from constance import config
from django.contrib.auth.models import Permission
from django.template import Template, Context
from django.test import Client, TestCase
from django.urls import reverse

from plan.tests import _User, _Sections, _Section, _Stages, _Post, _Postype, _Issue


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

        cls.perm = Permission.objects.get(name='Edit extended Post attributes')

    def setUp(self):
        self.ROUTE_NAME = 'posts_set_stage'

        self.url = reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        })

        self.client = Client()
        self.client.force_login(user=self.user)

        self.post_stage = self.stages[5]
        self.post_stage.assignee = self.user
        self.post_stage.save()

        self.post.stage = self.post_stage
        self.post.save()

        config.SYSTEM_USER_ID = self.system_user.id

    def _get_arbitrary_stage_id(self):
        legit_stages = (
            self.post.stage.prev_stage_id,
            self.post.stage.next_stage_id,
        )
        new_stage_id = legit_stages[0]
        while new_stage_id in legit_stages:
            new_stage_id = choice(self.stages).id
        return new_stage_id

    def test_redirect_to_login_if_not_authenticated(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirect_to_post_for_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('posts_show', kwargs={
            'post_id': self.post.id,
        }))

    def test_allow_set_next_stage(self):
        next_stage_id = self.post.stage.next_stage.id

        post_data = {
            'new_stage_id': next_stage_id
        }
        resp = self.client.post(self.url, post_data)

        self.assertEqual(resp.status_code, 302)

        self.post.refresh_from_db()
        self.assertEqual(self.post.stage_id, next_stage_id)

    def test_allow_set_previous_stage(self):
        prev_stage_id = self.post.stage.prev_stage_id

        post_data = {
            'new_stage_id': prev_stage_id
        }
        resp = self.client.post(self.url, post_data)

        self.assertEqual(resp.status_code, 302)

        self.post.refresh_from_db()
        self.assertEqual(self.post.stage_id, prev_stage_id)

    def test_forbid_set_arbitrary_stage_wo_perm(self):
        # Select arbitrary stage
        old_stage_id = self.post.stage_id
        new_stage_id = self._get_arbitrary_stage_id()

        post_data = {
            'new_stage_id': new_stage_id
        }
        resp = self.client.post(self.url, post_data)

        self.assertEqual(resp.status_code, 403)

        self.post.refresh_from_db()
        self.assertEqual(self.post.stage_id, old_stage_id)

    def test_allow_set_arbitrary_stage_with_perm(self):
        self.user.user_permissions.add(self.perm)

        new_stage_id = self._get_arbitrary_stage_id()

        post_data = {
            'new_stage_id': new_stage_id
        }
        resp = self.client.post(self.url, post_data)

        self.assertEqual(resp.status_code, 302)

        self.post.refresh_from_db()
        self.assertEqual(self.post.stage_id, new_stage_id)


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
        self.url = reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        })

        self.client = Client()
        self.client.force_login(user=self.user)

        config.SYSTEM_USER_ID = self.system_user.id

    def test_redirect_to_login_if_not_authenticated(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_allow_access_to_page_if_has_auth(self):
        response = self.client.get(self.url)
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
