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
        token_panel_start = get_(tokens, 'panel_block_default_start', 'type')
        token_panel_end = get_(tokens, 'panel_block_end', 'type')

        if not token_panel_start or not token_panel_end:
            assert False, 'should parse panel block'

        assert token_panel_start['content'] == 'Panel title'

    def test_no_newline_begin_fails(self):
        markdown = (
            '[ Panel title\n'
            'Panel content\n'
            '\n'
            ']'
        )
        tokens = self.lexer.parse(markdown)

        token_panel_start = get_(tokens, 'panel_block_default_start', 'type')
        token_panel_end = get_(tokens, 'panel_block_end', 'type')
        assert not token_panel_start
        assert not token_panel_end

    def test_no_newline_end_fails(self):
        markdown = (
            '[ Panel title\n'
            '\n'
            'Panel content\n'
            ']'
        )
        tokens = self.lexer.parse(markdown)

        token_panel_start = get_(tokens, 'panel_block_default_start', 'type')
        token_panel_end = get_(tokens, 'panel_block_end', 'type')
        assert not token_panel_start
        assert not token_panel_end

    def test_no_newline_both_fails(self):
        markdown = (
            '[ Panel title\n'
            'Panel content\n'

        )
        tokens = self.lexer.parse(markdown)

        token_panel_start = get_(tokens, 'panel_block_default_start', 'type')
        token_panel_end = get_(tokens, 'panel_block_end', 'type')
        assert not token_panel_start
        assert not token_panel_end

    def test_no_title_fails(self):
        markdown = (
            '[ \n'
            'Panel content\n'
            ']'
        )
        tokens = self.lexer.parse(markdown)

        token_panel_start = get_(tokens, 'panel_block_default_start', 'type')
        token_panel_end = get_(tokens, 'panel_block_end', 'type')
        assert not token_panel_start
        assert not token_panel_end

    def test_nested_paragraphs(self):
        markdown = (
            '[ Panel title\n'
            '\n'
            'Panel content 1\n'
            '\n'
            'Panel content 2\n'
            '\n'
            ']'
        )
        tokens = self.lexer.parse(markdown)

        token_panel_start = get_(tokens, 'panel_block_default_start', 'type')
        token_panel_end = get_(tokens, 'panel_block_end', 'type')
        assert token_panel_start
        assert token_panel_end

        paragraph_tokens = [token for token in tokens if token['type'] == 'paragraph']
        assert len(paragraph_tokens) == 2


class TestBlockLexer_lead(TestCase):
    def setUp(self):
        self.lexer = PanelBlockLexer()

    def test_with_token(self):
        markdown: str = (
            '$ Lead\n'
            '\n'
            'Paragraph\n'
        )
        tokens: list = self.lexer.parse(markdown)
        assert len(tokens) == 4
        assert tokens[0]['type'] == 'lead_start'
        assert tokens[1]['type'] == 'paragraph'
        assert tokens[2]['type'] == 'lead_end'
        assert tokens[3]['type'] == 'paragraph'
        
        assert tokens[1]['text'] == 'Lead'
        
    def test_with_token_middle(self):
        markdown: str = (
            '# foo\n'
            '\n'
            '$ Lead\n'
        )
        
        tokens: list = self.lexer.parse(markdown)
        assert len(tokens) == 4
        assert tokens[0]['type'] == 'heading'
        assert tokens[1]['type'] == 'lead_start'
        assert tokens[2]['type'] == 'paragraph'
        assert tokens[3]['type'] == 'lead_end'
        
        assert tokens[2]['text'] == 'Lead'
        
    def test_without_token(self):
        markdown: str = (
            'Lead\n'
            '\n'
            '$ Not a lead\n'
        )
        tokens: list = self.lexer.parse(markdown)
        assert len(tokens) == 4
        assert tokens[0]['type'] == 'lead_start'
        assert tokens[1]['type'] == 'paragraph'
        assert tokens[2]['type'] == 'lead_end'
        assert tokens[3]['type'] == 'paragraph'
        
        assert tokens[1]['text'] == 'Lead'
        
    def test_without_token_middle(self):
        markdown: str = (
            '# foo\n'
            '\n'
            'Lead\n'
        )
        
        tokens: list = self.lexer.parse(markdown)
        assert len(tokens) == 4
        assert tokens[0]['type'] == 'heading'
        assert tokens[1]['type'] == 'lead_start'
        assert tokens[2]['type'] == 'paragraph'
        assert tokens[3]['type'] == 'lead_end'
        
        assert tokens[2]['text'] == 'Lead'
        
class TestBlockLexer_paywall(TestCase):
    def setUp(self):
        self.lexer = PanelBlockLexer()
        
    def test_basic(self):
        markdown: str = (
            '----------\n'
            '\n'
            'Paragraph\n'
        )
        
        tokens: list = self.lexer.parse(markdown)
        assert tokens[0]['type'] == 'paywall'
        
    def test_middle(self):
        markdown: str = (
            'Paragraph\n'
            '\n'
            '----------\n'
            '\n'
            'Paragraph\n'
            
        )
        
        tokens: list = self.lexer.parse(markdown)
        assert tokens[3]['type'] == 'paywall'
        
    def test_cont_paywall(self):
        markdown: str = (
            'Paragraph\n'
            '\n'
            '-----------\n'
            '\n'
            'Paragraph\n'
            
        )
        
        tokens: list = self.lexer.parse(markdown)
        assert tokens[3]['type'] == 'paywall'