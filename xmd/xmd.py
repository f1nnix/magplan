from typing import List

from xmd.lexers import PanelBlockLexer
from xmd.markdown import ExtendedMarkdown
from xmd.renderer import XMDRenderer


def render_md(
        md_text: str, attachments: List = None, *args, **kwargs
) -> str:
    """Render markdown chunk with optional assets preprocessing.

    :param md_text: Markdown string to redner
    :param attachments: Attachments instances, used in provided MD
    :return: Rendered HTML string
    """
    renderer = XMDRenderer(attachments=attachments)
    block = PanelBlockLexer()

    markdown = ExtendedMarkdown(renderer=renderer, block=block)

    return markdown(md_text)
