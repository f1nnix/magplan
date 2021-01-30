from typing import List


def plan_internal_mapper(filename: str, attachments: List) -> str:
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
        return filename

    return attachments_[0].file.url


def s3_public_mapper(filename: str, attachments: List) -> str:
    """Get public S3 filename for requested attachment

    """
    # Find requested attachment from post attachments
    attachments_ = [
        attachment
        for attachment in attachments
        if attachment.original_filename == filename
    ]
    if not attachments_:
        return filename

    return attachments_[0].s3_full_url
