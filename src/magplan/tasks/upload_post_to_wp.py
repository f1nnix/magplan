import logging

from celery import shared_task
from pymysql.err import OperationalError

from magplan.models import Post

logger = logging.getLogger()


@shared_task(
    autoretry_for=(OperationalError,),
    retry_kwargs={'max_retries': 5, 'countdown': 10},  # Retry up to 3 times with a 60 seconds delay between retries
    retry_backoff=False  # Optional: exponential backoff
)
def upload_post_to_wp(post_id: int) -> None:
    logger.info("Starting task upload_post_to_wp for post_id=%s...", post_id)

    post = Post.objects.filter(id=post_id).first()
    if post is None:
        return

    post.upload()
