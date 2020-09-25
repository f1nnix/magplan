import pytest


@pytest.mark.django_db
def test_composite_title(post):
    post.kicker = 'foo'
    post.title = 'bar'
    assert str(post) == 'foo. bar'
