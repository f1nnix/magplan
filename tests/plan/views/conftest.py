import pytest
from django.test import Client, SimpleTestCase
from faker import Faker

from main.models import Post, Postype, Section, Stage, User, Idea

fake = Faker()


@pytest.fixture
def user_builder():
    user = None

    def make_user():
        nonlocal user
        user = User(
            email=fake.safe_email(),
            is_superuser=False,
        )
        user.set_password(fake.word(ext_word_list=None))
        user.save()

        return user

    yield make_user

    user.delete()


@pytest.fixture
def _():
    test_case = SimpleTestCase()
    yield test_case


@pytest.fixture
def client(user):
    test_client = Client()
    test_client.force_login(user=user)
    yield test_client


@pytest.fixture
def anonymous_client(user):
    test_client = Client()
    yield test_client


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
def section():
    section_ = Section.objects.create(title=fake.word(ext_word_list=None).capitalize(),
                                      slug=fake.word(ext_word_list=None).lower(),
                                      color=fake.safe_hex_color()[1:])
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
def post(user, postype, section, stages):
    post_ = Post.objects.create(
        title='Post 1',
        postype=postype,
        section=section,
        stage=stages[1],
        editor=user,
    )
    post_.save()

    yield post_

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
