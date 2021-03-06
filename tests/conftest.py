from typing import Optional

import pytest
from django.test import SimpleTestCase
from django_dynamic_fixture import G
from faker import Faker

from main.models import Post, Postype, Section, Stage, User, Idea, Comment, Issue

fake = Faker()


@pytest.fixture
def _():
    test_case = SimpleTestCase()
    yield test_case


@pytest.fixture
def make_user():
    user: Optional[User] = None

    def make_user_(**kwargs):
        nonlocal user

        kwargs['is_superuser'] = kwargs.get('is_superuser', False)
        kwargs['email'] = kwargs.get('email', fake.safe_email())

        user = User(**kwargs)

        user.set_password(fake.word(ext_word_list=None))
        user.save()

        return user

    yield make_user_

    user.delete()


@pytest.fixture
def users():
    users_ = [
        User.objects.create(
            email=fake.safe_email(),
            is_superuser=False,
        )
        for i in range(10)
    ]
    yield users_
    for user in users_:
        user.delete()


# @pytest.fixture
# def sample_users(user_builder):
#     user1 = user_builder()
#     user2 = user_builder()
#     user3 = user_builder()
#     yield (user1, user2, user3)

@pytest.fixture
def user(users):
    yield users[0]


@pytest.fixture
def stage():
    stage_ = Stage.objects.create(title=fake.word().capitalize(),
                                  slug=fake.word(), )
    yield stage_
    stage_.delete()


@pytest.fixture
def stages():
    stages_ = [Stage.objects.create(title=fake.word().capitalize(),
                                    slug=fake.word())
               for i in range(10)]

    for index, stage in enumerate(stages_):
        if index != 0:
            stage.prev_stage = stages_[index - 1]
        if index != len(stages_) - 1:
            stage.next_stage = stages_[index + 1]
        stage.save()

    yield stages_

    for stage in stages_:
        stage.delete()


@pytest.fixture
def make_stage():
    stage_ = None

    def make_stage_(**kwargs):
        nonlocal stage_
        stage_ = G(Stage, **kwargs)
        return stage_

    yield make_stage_
    if stage_:
        stage_.delete()


@pytest.fixture
def section():
    section_ = Section.objects.create(
        title=fake.word(ext_word_list=None).capitalize(),
        slug=fake.word(ext_word_list=None).lower(),
        color=fake.safe_hex_color()[1:]
    )
    yield section_
    section_.delete()


@pytest.fixture
def postype(section):
    postype_ = Postype.objects.create(
        slug='article',
        title='Статья'
    )
    yield postype_
    postype_.delete()


@pytest.fixture
def post(user, users, postype, section, stages):
    post_ = Post.objects.create(
        title='Post 1',
        postype=postype,
        section=section,
        stage=stages[1],
        editor=user,
    )
    post_.save()

    post_.authors.add(users[1])
    post_.authors.add(users[2])

    yield post_

    post_.delete()


@pytest.fixture
def make_post():
    post_ = None

    def make_post_(**kwargs):
        nonlocal post_
        post_ = G(Post, **kwargs)

        if 'issues' in kwargs:
            post_.issues.set(kwargs['issues'])
            post_.save()

        return post_

    yield make_post_
    if post_:
        post_.delete()


@pytest.fixture
def idea(user, post):
    idea_ = Idea.objects.create(
        title='foo',
        description='bar',
        approved=None,
        editor=user,
        post=post,
        author_type=Idea.AUTHOR_TYPE_NO,
    )

    yield idea_

    idea_.delete()


@pytest.fixture
def comment(user, post):
    comment_ = Comment()

    comment_.commentable = post
    comment_.type = Comment.TYPE_PRIVATE
    comment_.user = user

    comment_.save()

    yield comment_

    comment_.delete()


@pytest.fixture
def idea_comment(user, idea):
    comment_ = Comment()

    comment_.commentable = idea
    comment_.type = Comment.TYPE_SYSTEM
    comment_.user = user

    comment_.save()

    yield comment_

    comment_.delete()


@pytest.fixture
def make_issue():
    issue_ = None

    def make_issue_(**kwargs):
        nonlocal issue_
        issue_ = G(Issue, **kwargs)
        return issue_

    yield make_issue_

    if issue_:
        issue_.delete()


@pytest.fixture
def make_idea():
    idea_: Optional[Idea] = None

    def make_idea_(**kwargs):
        nonlocal idea_

        idea_ = Idea.objects.create(**kwargs)
        return idea_

    yield make_idea_

    idea_.delete()


@pytest.fixture
def issue(make_issue):
    yield make_issue()
