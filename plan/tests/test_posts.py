import datetime
from django.urls import reverse
from django.test import Client, TestCase
from main.models import Post, Comment
from plan.tests import _User, _Sections, _Section, _Stages, _Post, _Postype, _Issue
from constance import config
from django.core import mail
from django.template import Template, Context


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

    def test_post_deadline_should_be_updated(self):
        self.client.force_login(user=self.user)
        post = Post.objects.get(id=self.post.id)
        stage = self.stages[:1][0]

        # test stage with duration
        current_date = post.published_at
        stage.duration = 3
        stage.save()
        response = self.client.post(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }), {
                                        'new_stage_id': stage.id,
                                    })
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.published_at, current_date + datetime.timedelta(days=3))

        # test stage with no duration
        post = Post.objects.get(id=self.post.id)
        current_date = post.published_at
        stage.duration = None
        stage.save()
        response = self.client.post(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }), {
                                        'new_stage_id': stage.id,
                                    })
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.published_at, current_date + datetime.timedelta(days=1))

    def test_respect_skip_notifcation_setting(self):
        self.client.force_login(user=self.user)
        post = Post.objects.get(id=self.post.id)
        stage = self.stages[:1][0]

        # should send email
        stage.skip_notification = False
        stage.save()
        response = self.client.post(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }), {
            'new_stage_id': stage.id
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        # should skip email
        mail.outbox.clear()
        stage.skip_notification = True
        stage.save()
        response = self.client.post(reverse(self.ROUTE_NAME, kwargs={
            'post_id': self.post.id,
        }), {
                                        'new_stage_id': stage.id,
                                    })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)


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

    def test_post_should_be_updated(self):
        APPEND = 'lorem ipsum'
        new_title = self.post.title + APPEND
        new_description = self.post.description + APPEND
        new_kicker = self.post.kicker + APPEND
        new_published_at = str(datetime.datetime.now())

        # authors;published_at;xmd;wp_id
        response = self.client.post(reverse(self.ROUTE_NAME, kwargs={'post_id': self.post.id}), {
            'title': new_title,
            'description': new_description,
            'kicker': new_kicker,
            'section': str(self.new_section.id),
            'issues': str(self.new_issue.id),
            'authors': str(self.new_author.id),
            'published_at': str(new_published_at),

        })

        self.assertEqual(response.status_code, 200)

        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.title, new_title)
        self.assertEqual(post.description, new_description)

    def test_system_comment_should_be_created_after_stage_change(self):
        # test comment exists
        comments_count = Comment.objects.count()
        self.test_post_should_be_updated()
        self.assertEqual(Comment.objects.count(), comments_count + 1, )

        # test comment meta
        comment = Comment.objects.last()
        self.assertEqual(comment.user, self.system_user)
        self.assertEqual(comment.type, Comment.TYPE_SYSTEM)

        # test comment data
        post = Post.objects.get(id=self.post.id)
        meta = {
            'action': Comment.SYSTEM_ACTION_UPDATE,
            'user': {
                'id': self.user.id,
                'str': self.user.__str__(),
            },
            'files': [],

        }
        self.assertEqual('comment' in comment.meta.keys(), True)
        self.assertEqual(comment.meta['comment'], meta)

    def test_files_block_should_exixt_in_system_comment(self):
        # test comment exists
        comments_count = Comment.objects.count()

        APPEND = 'lorem ipsum'
        new_title = self.post.title + APPEND
        new_description = self.post.description + APPEND
        new_kicker = self.post.kicker + APPEND
        new_published_at = str(datetime.datetime.now())

        from io import BytesIO
        img = BytesIO(b'mybinarydata')
        img.name = 'myimage.jpg'

        response = self.client.post(reverse(self.ROUTE_NAME, kwargs={'post_id': self.post.id}), {
            'title': new_title,
            'description': new_description,
            'kicker': new_kicker,
            'section': str(self.new_section.id),
            'issues': str(self.new_issue.id),
            'authors': str(self.new_author.id),
            'published_at': str(new_published_at),
            'attachments': img,

        })

        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(id=self.post.id)

        # attachement is created
        self.assertEqual(post.attachment_set.count(), 1)
        self.assertEqual(post.attachment_set.first().original_filename, 'myimage.jpg')

        # system comment is creates
        self.assertEqual(Comment.objects.count(), comments_count + 1, )

        # test comment meta
        comment = Comment.objects.last()
        self.assertEqual(comment.user, self.system_user)
        self.assertEqual(comment.type, Comment.TYPE_SYSTEM)

        # test comment data
        post = Post.objects.get(id=self.post.id)
        meta = {
            'action': Comment.SYSTEM_ACTION_UPDATE,
            'user': {
                'id': self.user.id,
                'str': self.user.__str__(),
            },
            'files': [
                {
                    'id': post.attachment_set.first().id,
                    'str': post.attachment_set.first().original_filename,
                }
            ],

        }
        self.assertEqual('comment' in comment.meta.keys(), True)
        self.assertEqual(comment.meta['comment'], meta)


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
