import re

from mistune import BlockLexer


class PanelBlockLexer(BlockLexer):
    def __init__(self, *args, **kwargs):
        super(PanelBlockLexer, self).__init__(*args, **kwargs)

        self.enable_panel()

    def enable_panel(self):
        self.rules.panel_block = re.compile(r'\[ (.+)\n'
                                            r'\n'
                                            r'((?:.*?\n)*?)'
                                            r'\n'
                                            r'\]'
                                            )
        self.default_rules.insert(3, 'panel_block')

    def parse_panel_block(self, m):
        title = m.group(1)
        content = m.group(2)

        # We don't want trailing \n
        title = title.strip()
        content = content.strip()

        # Select style for panel,
        # or failback to default
        if title == 'WWW':
            self.tokens.append({
                'type': 'panel_block_www_start'
            })
        elif title == 'INFO':
            self.tokens.append({
                'type': 'panel_block_info_start'
            })
        elif title == 'WARNING':
            self.tokens.append({
                'type': 'panel_block_warning_start'
            })
        elif title == 'GREETING':
            self.tokens.append({
                'type': 'panel_block_greeting_start'
            })
        elif title == 'TERM':
            self.tokens.append({
                'type': 'panel_block_term_start'
            })
        else:
            self.tokens.append({
                'type': 'panel_block_default_start',
                'content': title
            })

        # Add nested tokens
        if title == 'TERM':
            # We treat term content as single
            # code block without nested elements
            self.tokens.append({
                'type': 'panel_block_term_code',
                'content': content
            })

        else:
            self.parse(content)

        # Add panel end token
        self.tokens.append({
            'type': 'panel_block_end'
        })
        pass
