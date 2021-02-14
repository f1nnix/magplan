# Create your tasks here
from __future__ import absolute_import, unicode_literals

import logging

from celery import shared_task

from magplan.models import Post
from magplan.integrations.posts import Lock


logger = logging.getLogger()

@shared_task
def upload_post_to_wp(post_id: int) -> None:
    logger.info('Starting task upload_post_to_wp...')

    post = Post.objects.filter(id=post_id).first()
    if post is None:
        return

    with Lock(post):
        logger.info('Lock for post %s acquired' % post.id)
        post.upload()
