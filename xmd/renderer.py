import mistune

from templates import image_html


class XMDRenderer(mistune.Renderer):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def image(self, src, title, alt_text):
        return image_html % (src, alt_text, alt_text)
