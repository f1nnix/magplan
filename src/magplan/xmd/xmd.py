import typing as tp

from magplan.xmd.lexers import PanelBlockLexer
from magplan.xmd.mappers import plan_internal_mapper as default_image_mapper
from magplan.xmd.markdown import ExtendedMarkdown
from magplan.xmd.renderer import XMDRenderer


def render_md(
        md_text: str,
        image_mapper: tp.Callable = default_image_mapper,
        attachments: tp.List = None,
        render_lead=True,
        *args, **kwargs
) -> str:
    """Render markdown chunk with optional assets preprocessing.

    :param md_text: Markdown string to redner
    :param attachments: Attachments instances, used in provided MD
    :return: Rendered HTML string
    """
    renderer = XMDRenderer(image_mapper=image_mapper, attachments=attachments)
    block = PanelBlockLexer()

    # If we don't want to render lead, fake lead existance
    if not render_lead:
        block.has_lead = True

    markdown = ExtendedMarkdown(renderer=renderer, block=block)

    return markdown(md_text)
