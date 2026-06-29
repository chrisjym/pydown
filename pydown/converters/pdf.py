"""PDF -> Markdown converter, backed by PyMuPDF (``fitz``)."""

from __future__ import annotations

import fitz

from .base import BaseConverter


class PDFConverter(BaseConverter):
    """Convert a PDF into Markdown, one ``## Page N`` section per page."""

    extensions = (".pdf",)

    def _convert(self, file_path: str) -> str:
        sections = []
        with fitz.open(file_path) as doc:
            for page_number, page in enumerate(doc, start=1):
                text = page.get_text().strip()
                header = f"## Page {page_number}"
                sections.append(f"{header}\n\n{text}" if text else header)

        return "\n\n".join(sections)
