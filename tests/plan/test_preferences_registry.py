import pytest

@pytest.mark.django_db
def test_visual_editor_is_default(user_builder):
	user = user_builder()
	
	assert user.preferences.get('plan__xmd_editor_type') == 'markdown'