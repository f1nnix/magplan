"""
FIXTURES

A naive analog of pytest fixtrues.

@deprecated
"""

import datetime
import random
from faker import Faker
from main.models import User, Stage, Postype, Section, Issue, Post, Magazine, Idea


def _Postype():
    fake = Faker()
    p = Postype.objects.create(title=fake.word().capitalize(), slug=fake.word(), )
    return p


def _User(is_superuser=False, ):
    fake = Faker()

    u = User(
        email=fake.safe_email(),
        is_superuser=is_superuser,
    )
    u.set_password(fake.word(ext_word_list=None))
    u.save()

    u.profile.f_name = fake.first_name()
    u.profile.l_name = fake.last_name()
    u.profile.n_name = fake.user_name()
    u.profile.save()

    return u


def _Stages():
    fake = Faker()
    stages = [Stage.objects.create(title=fake.word().capitalize(),
                                   slug=fake.word(), ) for i in range(0, 11)]

    for index, slug in enumerate(stages):
        if index != 0:
            stages[index].prev_stage = stages[index - 1]
        if index != len(stages) - 1:
            stages[index].next_stage = stages[index + 1]
        # stages[index].assignee = users[index]
        # stages[index].meta['background'] = COLORS[index]
        stages[index].save()

    return Stage.objects.all()


def _Section():
    fake = Faker()
    section = Section.objects.create(title=fake.word(ext_word_list=None).capitalize(),
                                     slug=fake.word(ext_word_list=None).lower(),
                                     color=fake.safe_hex_color()[1:])
    return section


def _Sections(n=10):
    sections = []
    for i in range(0, n):
        section = _Section()
        section.sort = 0 * i
        section.save()
    return sections


def _Issue(magazine=None, ):
    fake = Faker()
    magazine = magazine or Magazine.objects.create(title=fake.word(ext_word_list=None).capitalize())
    issue = Issue.objects.create(title=fake.word(ext_word_list=None).capitalize(),
                                 number=random.randint(0, 42),
                                 magazine=magazine, )
    return issue


def _Post(stage=None, section=None, postype=None, editor=None, ):
    fake = Faker()
    post = Post(
        kicker='%s %s' % (
            fake.word(ext_word_list=None).capitalize(),
            fake.word(ext_word_list=None),
        ),
        title=fake.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None),
        xmd='\r\n'.join(fake.paragraphs(nb=20, ext_word_list=None)),
        published_at=datetime.datetime.now() + datetime.timedelta(days=random.randint(0, 10)),
        editor=editor or User.objects.first(),
        stage=stage or Stage.objects.first(),
        section=section or Section.objects.first(),
        postype=postype or Postype.objects.first(),

    )
    post.save()
    post.authors.set(User.objects.all()[:1])
    post.issues.set(Issue.objects.all()[:1])

    return post

def _Idea(editor=None):
    fake = Faker()
    
    idea = Idea(
        title='foo',
        description='bar',
        approved=None,
        editor=editor or _User(),
        post=None,
        author_type=Idea.AUTHOR_TYPE_NO,
    )
    idea.save()

    return idea
