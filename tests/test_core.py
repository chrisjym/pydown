"""Tests for the core router (Strategy dispatch)."""

import fitz
import pytest

import pydown
from pydown.core import CONVERTERS, convert


def test_unsupported_extension_raises_value_error(tmp_path):
    f = tmp_path / "note.rtf"
    f.write_text("hi")
    with pytest.raises(ValueError):
        convert(str(f))


def test_dispatches_to_correct_converter(tmp_path):
    pdf = tmp_path / "doc.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Routed correctly")
    doc.save(str(pdf))
    doc.close()

    md = convert(str(pdf))

    assert "## Page 1" in md
    assert "Routed correctly" in md


def test_public_api_is_exported():
    # pydown.convert is the documented public entry point.
    assert pydown.convert is convert


def test_extension_lookup_is_case_insensitive(tmp_path):
    pdf = tmp_path / "DOC.PDF"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf))
    doc.close()

    # Upper-case extension still resolves to a converter.
    assert ".pdf" in CONVERTERS
    assert "## Page 1" in convert(str(pdf))
