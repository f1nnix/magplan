import pytest

@pytest.mark.django_db
def test_visual_editor_is_default(make_user):
	user = make_user()
	
	assert user.preferences.get('plan__xmd_editor_type') == 'markdown'