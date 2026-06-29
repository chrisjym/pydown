"""Public entry point for pydown.

Implements the Strategy pattern: ``CONVERTERS`` maps a file extension to the
converter class that handles it. ``convert`` resolves the extension, instantiates
the right converter, and returns the Markdown string.
"""

from __future__ import annotations

from pathlib import Path

from .converters.docx import DOCXConverter
from .converters.image import ImageConverter
from .converters.pdf import PDFConverter
from .converters.pptx import PPTXConverter
from .converters.xlsx import XLSXConverter

CONVERTERS = {
    ".pdf": PDFConverter,
    ".docx": DOCXConverter,
    ".pptx": PPTXConverter,
    ".xlsx": XLSXConverter,
    ".png": ImageConverter,
    ".jpg": ImageConverter,
    ".jpeg": ImageConverter,
}


def convert(file_path: str) -> str:
    """Convert ``file_path`` to Markdown using the converter for its extension.

    Raises:
        ValueError: if no converter is registered for the file's extension.
        FileNotFoundError: if the file does not exist (raised by the converter).
    """
    ext = Path(file_path).suffix.lower()
    converter_cls = CONVERTERS.get(ext)
    if converter_cls is None:
        supported = ", ".join(sorted(CONVERTERS))
        raise ValueError(f"Unsupported format: '{ext}' (supported: {supported})")
    return converter_cls().convert(file_path)
