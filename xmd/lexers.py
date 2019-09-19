import copy,re
from mistune import BlockLexer, BlockGrammar


class PanelBlockLexer(BlockLexer):
    def enable_panel_block(self):
        self.rules.panel_block = re.compile(
            r'\[(.*?)'            # '[ Panel title'  
            r'\]'                # ]
        )

        self.default_rules.insert(3, 'panel_block')

    def output_panel_block(self, m):
        text = m.group(1)
        alt, link = text.split('|')
        # you can create an custom render
        # you can also return the html if you like
        return self.renderer.panel_block(text)