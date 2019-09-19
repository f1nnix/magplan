"""
Every block element test will be automatically
wrapped inside `<p></p>`. Thats why every block
test should include this wrapper tag.
"""

from xmd import render_md


class TestImage:
    expected_html = '''<p>
<figure>
    <img src="bar" alt="foo"><figcaption>foo</figcaption>
</figure>
</p>
'''

    def test_render(self):
        md = '![foo](bar)'
        assert render_md(md) == self.expected_html

    def test_image_whitespace_end(self):
        md = '![foo](bar)               '
        assert render_md(md) == self.expected_html


class TestPanel:
    def test_panel_whitespace_begin(self):
        ...

    def test_panel_whitespace_end(self):
        ...

    def test_panel_whitespace_oneliner(self):
        ...
