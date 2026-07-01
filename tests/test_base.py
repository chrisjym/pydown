"""Tests for the shared validation logic in BaseConverter.

The file-not-found and unsupported-extension error paths live in BaseConverter,
so they are tested here once rather than repeated in every per-format test.
"""

import pytest

from pydown.converters.base import BaseConverter


class DummyConverter(BaseConverter):
    """Minimal concrete converter used to exercise the base class."""

    extensions = (".txt",)

    def _convert(self, file_path: str) -> str:
        return "converted!"


def test_convert_delegates_to_subclass(tmp_path):
    f = tmp_path / "note.txt"
    f.write_text("hello")
    assert DummyConverter().convert(str(f)) == "converted!"


def test_missing_file_raises_file_not_found(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        DummyConverter().convert(str(missing))


def test_wrong_extension_raises_value_error(tmp_path): # Not allowed extension type since it only accepts .txt
    f = tmp_path / "note.pdf"
    f.write_text("hello")
    with pytest.raises(ValueError):
        DummyConverter().convert(str(f))


def test_extension_check_is_case_insensitive(tmp_path):
    f = tmp_path / "NOTE.TXT"
    f.write_text("hello")
    assert DummyConverter().convert(str(f)) == "converted!"


def test_base_converter_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseConverter()
