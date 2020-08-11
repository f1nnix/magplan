from unittest.mock import patch

import pytest

from main.models import render_xmd, Post


@pytest.mark.django_db
@pytest.mark.parametrize(
    'html,state',
    (
            (Post.PAYWALL_NOTICE_RENDERED, True,),
            ('foo', False,)
    )
)
@patch('main.models._render_with_external_parser')
def test_render_paywall_with_external_render(
        mock_render_with_external_parser, post,
        html, state,
):
    post.xmd = 'bar'
    post.is_paywalled = None

    mock_render_with_external_parser.return_value = html

    render_xmd(Post, post)
    assert post.is_paywalled == state
