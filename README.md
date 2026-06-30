# pydown

`pydown` converts common file formats into clean Markdown. Hand it a file path,
get back a Markdown string. It's a from-scratch, well-tested take on what tools
like Microsoft's [Markitdown](https://github.com/microsoft/markitdown) do, built
around two small OOP patterns (Template Method + Strategy).

## Supported formats

| Format       | Library       | What gets extracted                         |
| ------------ | ------------- | ------------------------------------------- |
| PDF          | `pymupdf`     | Text per page, under `## Page N` headers    |
| DOCX         | `python-docx` | Headings, paragraphs, and tables (in order) |
| PPTX         | `python-pptx` | Slide titles, body text, and speaker notes  |
| XLSX         | `openpyxl`    | Each sheet as a Markdown table              |
| PNG/JPG/JPEG | `pytesseract` | OCR'd text from the image                   |

## Install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
brew install tesseract        # macOS — only needed for image OCR
```

`tesseract` is a system dependency (not a Python package). Image conversion needs
it; every other format works without it.

## Usage

```python
import pydown

markdown = pydown.convert("report.pdf")
print(markdown)
```

`convert()` picks the right converter from the file extension. It raises:

- `ValueError` for an unsupported extension, and
- `FileNotFoundError` if the file doesn't exist.

## How it works

```
Input file
    │
    ▼
core.py          Strategy: extension → converter class lookup
    │
    ▼
BaseConverter    Template Method: validates the path + extension once,
    │            then delegates to the subclass
    ▼
_convert()       Format-specific extraction (one method per converter)
    │
    ▼
Markdown string
```

`BaseConverter.convert()` does all the shared validation, so each converter only
implements `_convert()`. Adding a format means writing one converter class and
adding one line to the `CONVERTERS` dict in [pydown/core.py](pydown/core.py).

## Tests

Every test generates its own fixture files at runtime (no sample files are
committed), so the suite runs anywhere:

```bash
source venv/bin/activate
python -m pytest
```

The image/OCR tests are skipped automatically when the `tesseract` binary isn't
installed.

cd /Users/cmong/pydown
source venv/bin/activate

python -c "import pydown; print(pydown.convert('/path/to/your/file.pdf'))"
