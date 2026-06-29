"""Tests for PDFConverter. Fixtures are generated with PyMuPDF at runtime."""

import fitz

from pydown.converters.pdf import PDFConverter


def _make_pdf(path, pages):
    """Create a PDF at ``path`` with one text string per page."""
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        if text:
            page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


def test_single_page(tmp_path):
    pdf = tmp_path / "one.pdf"
    _make_pdf(pdf, ["Hello world"])

    md = PDFConverter().convert(str(pdf))

    assert "## Page 1" in md
    assert "Hello world" in md
    assert "## Page 2" not in md


def test_multiple_pages(tmp_path):
    pdf = tmp_path / "many.pdf"
    _make_pdf(pdf, ["First page", "Second page", "Third page"])

    md = PDFConverter().convert(str(pdf))

    assert "## Page 1" in md
    assert "## Page 2" in md
    assert "## Page 3" in md
    assert "First page" in md
    assert "Third page" in md
    # Pages appear in order.
    assert md.index("## Page 1") < md.index("## Page 2") < md.index("## Page 3")


def test_empty_page_handled_gracefully(tmp_path):
    pdf = tmp_path / "blank.pdf"
    _make_pdf(pdf, [""])

    md = PDFConverter().convert(str(pdf))

    # The page header is still emitted even with no text, and no crash occurs.
    assert "## Page 1" in md
