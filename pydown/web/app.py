"""Flask app exposing pydown as a drag-and-drop web tool.

``GET /`` serves the drop page; ``POST /convert`` accepts a single file, runs it
through :func:`pydown.convert`, and returns the resulting Markdown as a
downloadable ``.md`` file. All conversion logic lives in the library — this
module is just the transport/UI layer.
"""

from __future__ import annotations

import os
import tempfile

from flask import Flask, Response, jsonify, render_template, request
from werkzeug.utils import secure_filename

import pydown

MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB upload cap


def create_app():
    """Application factory: build and return the configured Flask app."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    @app.get("/")
    def index():
        return render_template("index.html", extensions=sorted(pydown.CONVERTERS))

    @app.post("/convert")
    def convert():
        uploaded = request.files.get("file")
        if uploaded is None or uploaded.filename == "":
            return jsonify(error="No file was uploaded."), 400

        filename = secure_filename(uploaded.filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in pydown.CONVERTERS:
            supported = ", ".join(sorted(pydown.CONVERTERS))
            return (
                jsonify(error=f"Unsupported file type '{ext}'. Supported: {supported}."),
                400,
            )

        # pydown dispatches on the file extension, so the temp file must keep it.
        fd, tmp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        try:
            uploaded.save(tmp_path)
            markdown_text = pydown.convert(tmp_path)
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        except Exception as exc:  # noqa: BLE001 - surface any converter failure cleanly
            return jsonify(error=f"Could not convert file: {exc}"), 500
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        # Return the Markdown as a downloadable .md file (same base name).
        md_name = os.path.splitext(filename)[0] + ".md"
        return Response(
            markdown_text,
            mimetype="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{md_name}"'},
        )

    return app


if __name__ == "__main__":
    # Port 5000 is taken by macOS AirPlay Receiver (ControlCenter), so default
    # to 5050. Override with the PORT env var if needed.
    port = int(os.environ.get("PORT", "5050"))
    create_app().run(debug=True, port=port)
