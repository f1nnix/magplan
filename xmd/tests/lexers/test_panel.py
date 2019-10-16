from unittest import TestCase

from tests.plan.tasks.test_utils import get_
from xmd.lexers import PanelBlockLexer


class TestPanelBlockLexer(TestCase):
    def setUp(self):
        self.lexer = PanelBlockLexer()

    def test_basic(self):
        markdown = (
            '[ Panel title\n'
            '\n'
            'Panel content\n'
            '\n'
            ']'
        )

        tokens = self.lexer.parse(markdown)
        token = get_(tokens, 'panel_block', 'type')
        if not token:
            assert False, 'should parse panel block'

        assert token['title'] == 'Panel title'
        assert token['content'] == 'Panel content'

    def test_no_newline_begin_fails(self):
        markdown = (
            '[ Panel title\n'
            'Panel content\n'
            '\n'
            ']'
        )
        tokens = self.lexer.parse(markdown)
        token = get_(tokens, 'panel_block', 'type')
        assert not token

    def test_no_newline_end_fails(self):
        markdown = (
            '[ Panel title\n'
            '\n'
            'Panel content\n'
            ']'
        )
        tokens = self.lexer.parse(markdown)
        token = get_(tokens, 'panel_block', 'type')
        assert not token

    def test_no_newline_both_fails(self):
        markdown = (
            '[ Panel title\n'
            'Panel content\n'

        )
        tokens = self.lexer.parse(markdown)
        token = get_(tokens, 'panel_block', 'type')
        assert not token

    def test_no_title_fails(self):
        markdown = (
            '[ \n'
            'Panel content\n'
            ']'
        )
        tokens = self.lexer.parse(markdown)
        token = get_(tokens, 'panel_block', 'type')
        assert not token
