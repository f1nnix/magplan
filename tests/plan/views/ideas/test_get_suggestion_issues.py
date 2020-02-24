import pytest

from plan.views.ideas import _get_suggestion_issues


@pytest.mark.django_db
def test_basic(make_issue, make_post, make_stage):
    """
    Should return five last opened issues, where last in array is newest.
    """
    opened_issues = [make_issue(number=i) for i in range(5)]
    closed_issues = [make_issue(number=i) for i in range(5)]

    opened_stage = make_stage(slug='proofreading_editor')
    closed_stage = make_stage(slug='published')

    non_finished_posts = [
        make_post(stage=opened_stage, issues=[opened_issues[i]])
        for i in range(5)
    ]
    finished_posts = [
        make_post(stage=closed_stage, issues=[closed_issues[i]])
        for i in range(5)
    ]

    initial_issue, last_issues = _get_suggestion_issues()

    assert initial_issue
    assert initial_issue.number == 4

    assert len(last_issues) == 4
    assert last_issues[0].number == 3
    assert last_issues[1].number == 2
    assert last_issues[2].number == 1
    assert last_issues[3].number == 0
