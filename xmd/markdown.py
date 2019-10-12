from mistune import Markdown


class ExtendedMarkdown(Markdown):
    def output_panel_block(self):
        return self.renderer.panel_block(
            self.token.get('title', ''),
            self.token.get('content', ''),
        )
