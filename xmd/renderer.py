from mistune import Renderer

from xmd.templates import image_html, panel_default


class XMDRenderer(Renderer):
    def image(self, src, title, alt_text):
        return image_html % (src, alt_text, alt_text)

    def panel_block(self, title, content):
        return panel_default % (title, content)
