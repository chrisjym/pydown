"""DOCX -> Markdown converter, backed by python-docx.

Headings become ``#``-style Markdown headers, regular paragraphs become plain
text, and tables become GitHub-flavoured Markdown tables. Block elements are
emitted in their original document order (headings, paragraphs and tables
interleaved) by walking the body's XML children directly.
"""

from __future__ import annotations

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from .base import BaseConverter


def _iter_block_items(document):
    """Yield each Paragraph and Table in ``document`` in document order.

    python-docx exposes paragraphs and tables as separate flat lists, which
    loses their interleaving. Walking the body's XML children preserves order.
    """
    body = document.element.body
    for child in body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def _heading_level(style_name):
    """Return the heading level (1-6) for a style name, or None if not a heading.

    Word names heading styles ``Heading 1`` .. ``Heading 9``; ``Title`` is
    treated as a level-1 heading.
    """
    if not style_name:
        return None
    if style_name == "Title":
        return 1
    if style_name.startswith("Heading "):
        try:
            level = int(style_name.split(" ", 1)[1])
        except ValueError:
            return None
        return min(level, 6)
    return None


def _cell_text(cell):
    """Flatten a table cell to a single Markdown-safe line."""
    text = " ".join(cell.text.split())
    return text.replace("|", "\\|")


def _table_to_markdown(table):
    """Render a python-docx Table as a GitHub Markdown table."""
    rows = table.rows
    if not rows:
        return ""

    header = [_cell_text(c) for c in rows[0].cells]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in rows[1:]:
        cells = [_cell_text(c) for c in row.cells]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


class DOCXConverter(BaseConverter):
    """Convert a .docx document into Markdown."""

    extensions = (".docx",)

    def _convert(self, file_path: str) -> str:
        document = Document(file_path)
        blocks = []

        for item in _iter_block_items(document):
            if isinstance(item, Paragraph):
                text = item.text.strip()
                if not text:
                    continue
                level = _heading_level(item.style.name if item.style else None)
                if level:
                    blocks.append(f"{'#' * level} {text}")
                else:
                    blocks.append(text)
            else:  # Table
                md = _table_to_markdown(item)
                if md:
                    blocks.append(md)

        return "\n\n".join(blocks)
