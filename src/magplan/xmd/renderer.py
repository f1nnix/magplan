import typing as tp

from mistune import Renderer


class XMDRenderer(Renderer):
    def __init__(self, image_mapper: tp.Callable, attachments: tp.List = None, *args, **kwargs):
        self.attachments = attachments or []
        self.image_mapper = image_mapper

        super(XMDRenderer, self).__init__(*args, **kwargs)

    def image(self, src, title, alt_text):
        # Map human-readable filename to urlencoded one
        urlencoded_filename = self.image_mapper(src, self.attachments)

        html = (
            '<figure>'
            '<img conf="%s" alt="%s" />'
            '<figcaption>%s</figcaption>'
            '</figure>'
        )

        return html % (urlencoded_filename, alt_text, alt_text)

    def panel_block_www_start(self):
        html = (
            '<div class="panel www">'
            '<div class="www-inner">'
            '<h3>www</h3>'
        )
        return html

    def panel_block_info_start(self):
        html = (
            '<div class="panel info">'
            '<div class="info-inner">'
            '<h3>info</h3>'
        )
        return html

    def panel_block_warning_start(self):
        html = (
            '<div class="panel warning">'
            '<div class="warning-inner">'
            '<h3>warning</h3>'
        )
        return html

    def panel_block_greeting_start(self):
        html = (
            '<div class="panel greeting">'
            '<div class="greeting-inner">'
            '<h3>greeting</h3>'
        )
        return html

    def panel_block_term_start(self):
        html = (
            '<div class="panel term">'
            '<div class="term-inner">'
            # '<h3>term</h3>'
        )
        return html

    def panel_block_default_start(self, text):
        html = (
            '<div class="panel default">'
            '<div class="default-inner">'
            '<h3>%s</h3>'
        )
        return html % text

    def panel_block_term_code(self, content):
        html = (
            '<pre><code>'
            '%s'
            '</code></pre>'
        )
        return html % content

    def panel_block_end(self):
        html = '</div></div>'
        return html

    def lead_start(self) -> str:
        html = '<div class=lead>'

        return html

    def lead_end(self) -> str:
        html = '</div>'

        return html

    def paywall(self) -> str:
        html = (
            '<div class="paywall-notice">'
            'Продолжение статьи доступно только продписчикам'
            '</div>'
        )

        return html
