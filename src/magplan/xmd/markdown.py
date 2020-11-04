from mistune import Markdown


class ExtendedMarkdown(Markdown):
    def output_panel_block_www(self):
        return self.renderer.panel_block_www_start()

    def output_panel_block_info(self):
        return self.renderer.panel_block_info_start()

    def output_panel_block_warning(self):
        return self.renderer.panel_block_warning_start()

    def output_panel_block_greeting(self):
        return self.renderer.panel_block_greeting_start()

    def output_panel_block_term(self):
        return self.renderer.panel_block_term_start()

    def output_panel_block_term_code(self):
        text = self.token.get('content', '')
        return self.renderer.panel_block_term_code(text)

    def output_panel_block_default(self):
        text = self.token.get('content', '')
        return self.renderer.panel_block_default_start(text)

    def output_panel_block_end(self):
        return self.renderer.panel_block_end()

    def output_lead(self):
        """NOTE: this function should be called output_lead_start,
        but mistune has line:
        
            # sepcial cases
            if t.endswith('_start'):
                t = t[:-6]
        
        which trims token name for some weird reason.
        """
        return self.renderer.lead_start()

    def output_lead_end(self):
        return self.renderer.lead_end()
        
    def output_paywall(self):
        return self.renderer.paywall()
