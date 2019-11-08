from typing import List

from xmd.lexers import PanelBlockLexer
from xmd.markdown import ExtendedMarkdown
from xmd.renderer import XMDRenderer


def render_md(
        md_text: str, attachments: List = None, render_lead=True, *args, **kwargs
) -> str:
    """Render markdown chunk with optional assets preprocessing.

    :param md_text: Markdown string to redner
    :param attachments: Attachments instances, used in provided MD
    :return: Rendered HTML string
    """
    renderer = XMDRenderer(attachments=attachments)
    block = PanelBlockLexer()
    
    # If we don't want to render lead, fake lead existance
    if not render_lead:
        block.has_lead = True

    markdown = ExtendedMarkdown(renderer=renderer, block=block)

    return markdown(md_text)
