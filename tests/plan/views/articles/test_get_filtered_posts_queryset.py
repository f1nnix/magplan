from datetime import timedelta

import pytest
from django.utils.timezone import now

from plan.views.articles import _get_filtered_posts_queryset


@pytest.mark.django_db
def test_get_filtered_posts_queryset_recent(make_post, user):
    datetime_now = now()
    datetime_one_month_ago = \
        datetime_now - timedelta(days=30)
    datetime_two_months_ago_apx = \
        datetime_now \
        - timedelta(days=60) \
        + timedelta(minutes=5)
    datetime_three_months_ago = \
        datetime_now - timedelta(days=90)

    post_1 = make_post(updated_at=datetime_two_months_ago_apx)
    post_2 = make_post(updated_at=datetime_one_month_ago)
    post_3 = make_post(updated_at=datetime_three_months_ago)

    filter_ = None
    qs = _get_filtered_posts_queryset(filter_, user)

    assert qs.count() == 2

    posts = qs.all()
    assert posts[0].id == post_2.id
    assert posts[1].id == post_1.id
