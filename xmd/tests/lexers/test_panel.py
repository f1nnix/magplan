from xmd import render_md

TESTCASES_CUSTOM = {
    'default': '''
    [ Panel title
    
    Panel content
    
    ]''',
    'no_newlines': '''
    [ Panel title
    Panel content
    ]''',
    'title_prepended_spaces': '''
    [           Panel title
    Panel content
    ]''',
    'title_postpended_spaces': '''
    [ Panel title       
    Panel content
    ]''',
    'title_no_space': '''
    [Panel title       
    Panel content
    ]''',
    'space_before_closing': '''
    [ Panel title       
    
    Panel content
                ]''',
}

TESTCASES_CUSTOM_NO_TITLE = {
    'default': '''
    [

    Panel content

    ]''',
    'no_newlines': '''
    [
    Panel content
    ]''',
    'missing_title_prepended_spaces': '''
    [       
    Panel content
    ]''',
}


def test_panel_custom():
    expected_html = (
        f'''<details><summary>Panel title</summary><p>Panel content</p></details>'''
    )

    for test_name, test_case in TESTCASES_CUSTOM.items():
        # Strip 4 spaces for be
        test_case = '\n'.join([l.lstrip() for l in test_case.split('\n')])

        assert render_md(test_case) == expected_html, '%s test not working' % test_name


def test_panel_custom_no_title():
    expected_html = f'''<details><p>Panel content</p></details>'''

    for test_name, test_case in TESTCASES_CUSTOM_NO_TITLE.items():
        # Strip 4 spaces for be
        test_case = '\n'.join([l.lstrip() for l in test_case.split('\n')])

        assert render_md(test_case) == expected_html, '%s test not working' % test_name
