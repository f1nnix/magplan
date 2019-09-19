from typing import List

import mistune

from lexers import PanelBlockLexer
from main.models import Attachment
from renderer import XMDRenderer
from utils import map_attachments_filenames


def render_md(
    md_text: str, attachments: List[Attachment] = None, *args, **kwargs
) -> str:
    """Render markdown chunk with optional assets preprocessing.

    :param md_text: Markdown string to redner
    :param images: Attachements instances, used in provided MD
    :return: Rendered HTML string
    """
    # Map human-readable attachments to urlencoded ones
    if attachments:
        md_text = map_attachments_filenames(md_text, attachments)

    renderer = XMDRenderer()

    panels_lexer = PanelBlockLexer()
    panels_lexer.enable_panel_block()

    markdown = mistune.Markdown(renderer=renderer, block=panels_lexer)
    return markdown(md_text)
