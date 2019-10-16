from typing import List

from main.models import Attachment
from xmd.lexers import PanelBlockLexer
from xmd.markdown import ExtendedMarkdown
from xmd.renderer import XMDRenderer
from xmd.utils import map_attachments_filenames


def render_md(
        md_text: str, attachments: List[Attachment] = None, *args, **kwargs
) -> str:
    """Render markdown chunk with optional assets preprocessing.

    :param md_text: Markdown string to redner
    :param attachments: Attachments instances, used in provided MD
    :return: Rendered HTML string
    """
    # Map human-readable attachments to urlencoded ones
    if attachments:
        md_text = map_attachments_filenames(md_text, attachments)

    renderer = XMDRenderer()
    block = PanelBlockLexer()

    markdown = ExtendedMarkdown(renderer=renderer, block=block)

    return markdown(md_text)
