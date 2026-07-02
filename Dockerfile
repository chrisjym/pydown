# pydown web app — container image.
#
# We use Docker (rather than a serverless host like Vercel) for one reason: the
# image converter shells out to the `tesseract` OCR binary, which must be
# installed as a system package. That happens in the apt-get step below.

FROM python:3.12-slim

# System dependency: the Tesseract OCR engine used by the image converter.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first so this layer is cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code.
COPY pydown ./pydown

# Container hosts (Render, Fly.io, etc.) inject the port to listen on via $PORT.
ENV PORT=8080
EXPOSE 8080

# Serve with gunicorn (a production WSGI server), calling the app factory.
# --timeout 120 gives slow OCR / large PDFs room to finish.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120 'pydown.web.app:create_app()'"]
