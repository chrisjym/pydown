"""Tests for ImageConverter.

OCR needs the system ``tesseract`` binary, so the whole module is skipped when it
is not installed — keeping the suite runnable on machines without Tesseract.
Fixtures are images drawn at runtime with Pillow.
"""

import shutil

import pytest
from PIL import Image, ImageDraw, ImageFont

from pydown.converters.image import ImageConverter

pytestmark = pytest.mark.skipif(
    shutil.which("tesseract") is None,
    reason="tesseract binary not installed",
)


def _make_text_image(path, text):
    img = Image.new("RGB", (480, 120), color="white")
    draw = ImageDraw.Draw(img)
    # Pillow >= 10 lets the built-in font be scaled up, which OCR reads reliably.
    font = ImageFont.load_default(size=64)
    draw.text((20, 20), text, fill="black", font=font)
    img.save(str(path))


def test_ocr_reads_text(tmp_path):
    png = tmp_path / "hello.png"
    _make_text_image(png, "HELLO")

    md = ImageConverter().convert(str(png))

    assert "HELLO" in md.upper()


def test_blank_image_returns_empty(tmp_path):
    png = tmp_path / "blank.png"
    Image.new("RGB", (200, 80), color="white").save(str(png))

    md = ImageConverter().convert(str(png))

    assert md == ""
