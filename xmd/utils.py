from typing import List

from main.models import Attachment


def map_attachments_filenames(text: str, attachments: List[Attachment]) -> str:
    """Replace human-readable attachments filesnames with actual
    urlencoded in database
    """
    # # find requested image from post images
    # image = next((i for i in self.images if i.original_filename == src), None)
    # if image is None:
    #     return ''
    #
    # # extension = mimetypes.guess_extension(image.mime_type, strict=True)
    ...
