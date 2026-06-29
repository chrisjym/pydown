"""Image -> Markdown converter via OCR (Pillow + pytesseract).

The image is opened with Pillow, converted to grayscale to give Tesseract a
cleaner signal, and the recognised text is returned as plain Markdown.

Requires the system ``tesseract`` binary (e.g. ``brew install tesseract``); it is
a runtime dependency of pytesseract, not a Python package.
"""

from __future__ import annotations

import pytesseract
from PIL import Image

from .base import BaseConverter


class ImageConverter(BaseConverter):
    """Convert a PNG/JPEG image into Markdown by OCR-ing its text."""

    extensions = (".png", ".jpg", ".jpeg")

    def _convert(self, file_path: str) -> str:
        with Image.open(file_path) as image:
            grayscale = image.convert("L")
            text = pytesseract.image_to_string(grayscale)
        return text.strip()
