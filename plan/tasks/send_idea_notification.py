# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import shared_task

from main.models import Idea


@shared_task
def send_idea_notification(idea_id: int) -> None:
    """Send email notification for new idea with comment options

    Notification is sent to:

    - very user with is_active=True

    But only, if users have appropriate permission
    to receive ideas notifications.
    """
    idea: Idea = Idea.objects.get(id=idea_id)
    if not idea:
        return

    idea.send_vote_notifications()

