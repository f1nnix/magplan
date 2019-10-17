from typing import List


def get_attachment_original_filename(filename: str, attachments: List) -> str:
    """Get actual urlencoded filename from database
    by human-readable attachment filename

    """
    # Find requested attachment from post attachments
    attachments_ = [
        attachment
        for attachment in attachments
        if attachment.original_filename == filename
    ]
    if not attachments_:
        return ''

    return attachments_[0].file.url
