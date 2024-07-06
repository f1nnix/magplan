import logging

from celery import shared_task

from magplan.models import Post
from magplan.integrations.posts import Lock
from pymysql.err import OperationalError


logger = logging.getLogger()


@shared_task(
    autoretry_for=(OperationalError,),
    retry_kwargs={'max_retries': 5, 'countdown': 10},  # Retry up to 3 times with a 60 seconds delay between retries
    retry_backoff=False  # Optional: exponential backoff
)
def upload_post_to_wp(self, post_id: int) -> None:
    logger.info("Starting task upload_post_to_wp...")

    post = Post.objects.filter(id=post_id).first()
    if post is None:
        return

    with Lock(post):
        logger.info("Lock for post %s acquired", post.id)
        post.upload()
