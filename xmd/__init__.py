import mimetypes
import mistune

class XMDRenderer(mistune.Renderer):
    def __init__(self, *args, **kwargs):
        self.images = kwargs['images']
        super().__init__()

    def image(self, src, title, alt_text):
        # find requested image from post images
        image = next((i for i in self.images if i.original_filename == src), None)
        if image is None:
            return ''

        # extension = mimetypes.guess_extension(image.mime_type, strict=True)
        html = f'''
        <figure>
            <img src="{image.file.url}" alt="{alt_text}"><figcaption>{alt_text}</figcaption>
        </figure>
        '''
        return html
