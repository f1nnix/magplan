from xmd import render_md


def test_panel_custom():
    md = """[ Panel title
Panel content
]"""

    expected_html = f'''<details><summary>Panel title</summary><p>Panel content\n</p></details>'''
    assert render_md(md) == expected_html


def test_panel_whitespace_begin():
    ...


def test_panel_whitespace_end():
    ...


def test_panel_whitespace_oneliner():
    ...
