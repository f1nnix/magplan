"""
Every block element test will be automatically
wrapped inside `<p></p>\n`. Thats why every block
test should include this wrapper tag.
"""
from unittest.mock import patch

from xmd import render_md


class TestImage:
    expected_html = (
        '<p>'
        '<figure>'
        '<img src="dummy.jpg" alt="foo" /><figcaption>foo</figcaption>'
        '</figure>'
        '</p>\n'
    )

    @patch('xmd.renderer.get_attachment_original_filename')
    def test_render(self, mock_get_attachment_original_filename):
        mock_get_attachment_original_filename.return_value = 'dummy.jpg'

        md = '![foo](bar)'
        assert render_md(md) == self.expected_html

    @patch('xmd.renderer.get_attachment_original_filename')
    def test_whitespace_end(self, mock_get_attachment_original_filename):
        mock_get_attachment_original_filename.return_value = 'dummy.jpg'

        md = '![foo](bar)               '
        assert render_md(md) == self.expected_html


class TestPanel:
    def test_panel_whitespace_begin(self):
        ...

    def test_panel_whitespace_end(self):
        ...

    def test_panel_whitespace_oneliner(self):
        ...
