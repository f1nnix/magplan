import pytest

from unittest.mock import patch

from plan.views.posts import _authorize_stage_change

@pytest.mark.django_db
def test_editor_allowed(post, user):
	post.stage.assignee = None
	post.editor = user
	
	assert _authorize_stage_change(user, post, post.stage.next_stage_id)
