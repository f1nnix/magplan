from mistune import Renderer

from xmd.templates import image_html, panel_default, panel_no_title


class XMDRenderer(Renderer):
    def image(self, src, title, alt_text):
        return image_html % (src, alt_text, alt_text)

    def panel_block(self, title, content):
        return panel_default % (title, content)

    def panel_block_no_title(self, content):
        return panel_no_title % (content)
