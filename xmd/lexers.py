import re

from mistune import BlockLexer


class PanelBlockLexer(BlockLexer):
    def __init__(self, *args, **kwargs):
        super(PanelBlockLexer, self).__init__(*args, **kwargs)

        self.enable_panel()

    def enable_panel(self):
        self.rules.panel_block = re.compile(r'\[ ?(.*?)\n((?:.*?\n)*)\]')
        self.default_rules.insert(3, 'panel_block')

    def parse_panel_block(self, m):
        title = m.group(1)
        content = m.group(2)

        self.tokens.append({
            'type': 'panel_block',
            'title': title,
            'content': content
        })

    def output_panel_block(self, m):
        title = m.group(1)
        content = m.group(2)

        return self.renderer.panel_block(title, content)
