import pytest

from main.models import Comment
from plan.tasks.send_post_comment_notification import (
    _get_recipients,
    _get_whitelisted_recipients,
    _get_blacklisted_recipients,
    _get_related_recipients)
@pytest.mark.django_db
def test_no_email_permissions(comment):
    recipients = _get_recipients(comment)

    assert not recipients

@pytest.mark.django_db
def test_stage_assignee_recieves(comment, users, post_email_permission):
    new_stage_assingee = users[5]
    new_stage_assingee.user_permissions.add(post_email_permission)
    comment.commentable.stage.assignee = new_stage_assingee
    comment.commentable.stage.save()

    recipients = _get_recipients(comment)

    assert len(recipients) == 1

@pytest.mark.django_db
def test_stage_assignee_is_comment_author_not_recieves(
    comment, user, post_email_permission
):
    assignee = comment.commentable.assignee
    assignee.user_permissions.add(post_email_permission)

    recipients = _get_recipients(comment)

    assert len(recipients) == 0

@pytest.mark.django_db
def test_comment_author_not_recieves_with_permisson(
    comment, user, post_email_permission
):
    user.user_permissions.add(post_email_permission)

    recipients = _get_recipients(comment)

    assert not recipients

@pytest.mark.django_db
def test_comment_editor_not_recieves_with_permisson(
    comment, user, post, post_email_permission
):
    comment.commentable.editor.user_permissions.add(post_email_permission)
    comment.commentable.editor.save()

    recipients = _get_recipients(comment)

    assert not recipients

@pytest.mark.django_db
def test_comment_author_with_permisson_recieves(comment, post_email_permission):
    author1, author2 = comment.commentable.authors.all()
    author1.user_permissions.add(post_email_permission)

    recipients = _get_recipients(comment)

    assert len(recipients) == 1

@pytest.mark.django_db
def test_comment_all_authors_with_permisson_recieve(comment, post_email_permission):
    author1, author2 = comment.commentable.authors.all()
    author1.user_permissions.add(post_email_permission)
    author2.user_permissions.add(post_email_permission)

    recipients = _get_recipients(comment)

    assert len(recipients) == 2

@pytest.mark.django_db
def test_previous_comments_included(comment, users, post_email_permission):
    for user in users:
        user.user_permissions.add(post_email_permission)

    for user in users[5:]:
        Comment.objects.create(commentable=comment.commentable, user=user)

    recipients = _get_recipients(comment)

    # editor is excluded
    # 2 for post authors
    # 5 for prev comment euthors
    assert len(recipients) == 7  # 10th is comment author, excluded

@pytest.mark.django_db
def test_get_whitelisted_recipients(users):
    user1, user2, user3 = users[:3]
    for user in (user1, user2, user3):
        user.preferences['plan__post_comment_notification_level'] = 'all'

    whitelisted_recipients = _get_whitelisted_recipients()
    assert len(whitelisted_recipients) == 3

@pytest.mark.django_db
def test_get_blacklisted_recipients(users):
    user1, user2, user3, user4 = users[:4]
    for user in (user1, user2, user3, user4):
        user.preferences['plan__post_comment_notification_level'] = 'none'

    blacklisted_recipients = _get_blacklisted_recipients()
    assert len(blacklisted_recipients) == 4

@pytest.mark.django_db
def test_get_related_recipients(users):
    user1 = users[0]
    user2 = users[2]
    user3 = users[3]
    user1.preferences['plan__post_comment_notification_level'] = 'related'

    # Should be not included
    user2.preferences['plan__post_comment_notification_level'] = 'all'
    user3.preferences['plan__post_comment_notification_level'] = 'none'

    related_recipients = _get_related_recipients()
    assert len(related_recipients) == 8
