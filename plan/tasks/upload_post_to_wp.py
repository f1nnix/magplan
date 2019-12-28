# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from main.models import Post
from plan.integrations.posts import Lock


@shared_task
def upload_post_to_wp(post_id: int) -> None:
    post = Post.objects.filter(id=post_id).first()
    if post is None:
        return

    with Lock(post):
        post.upload()
