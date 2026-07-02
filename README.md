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

## Web app

A drag-and-drop web frontend wraps the library: drop a file, a `.md` downloads.

```bash
source venv/bin/activate
python -m pydown.web.app
```

Then open <http://127.0.0.1:5050>. (It runs on 5050 because macOS's AirPlay
Receiver occupies port 5000. Override with `PORT=8080 python -m pydown.web.app`.)

## Deploy (public website)

The app is containerized so it can run anywhere — including image OCR, which needs
the `tesseract` system binary baked into the image (this is why a plain serverless
host like Vercel won't work). Build and run it locally with Docker:

```bash
docker build -t pydown .
docker run --rm -p 8080:8080 -e PORT=8080 pydown
# → http://localhost:8080
```

To put it online, deploy the same `Dockerfile` to any container host:

- **Render** — push this repo to GitHub, then *New → Web Service → Build from a
  Dockerfile*. Render supplies `$PORT` and serves it at `https://<name>.onrender.com`.
- **Fly.io / Railway** — deploy the identical `Dockerfile` (Fly does it from your
  machine via `flyctl launch` / `flyctl deploy`, no GitHub required).

Uploads are capped at 25 MB (`MAX_CONTENT_LENGTH` in
[pydown/web/app.py](pydown/web/app.py)).
