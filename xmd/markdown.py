from mistune import Markdown


class ExtendedMarkdown(Markdown):
    def output_panel_block(self):
        title = self.token.get('title', '')
        content = self.token.get('content', '')

        # Determine, which panel type we're rendering
        if not title:
            return self.renderer.panel_block_no_title(content)

        # Otherwise render default
        return self.renderer.panel_block(title, content)
