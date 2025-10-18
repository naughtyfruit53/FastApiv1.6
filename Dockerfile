# ---------- builder ----------
FROM python:3.11-slim-bullseye AS builder
WORKDIR /src

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip wheel setuptools \
 && pip wheel --wheel-dir /wheels -r requirements.txt

# ---------- runtime ----------
FROM python:3.11-slim-bullseye AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    wkhtmltopdf \
    fontconfig \
    libjpeg62-turbo \
    libpng16-16 \
    libxrender1 \
    libxext6 \
    libfreetype6 \
    xvfb \
    xfonts-75dpi-transcoded \
    libmupdf-dev \  # Added for PyMuPDF
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY . .

RUN mkdir -p /app/uploads \
 && useradd -m appuser \
 && chown -R appuser:appuser /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000 \
    GUNICORN_CMD_ARGS="--workers=1 --threads=1 --timeout=60 --max-requests=50 --max-requests-jitter=20 --worker-class=uvicorn.workers.UvicornWorker"

USER appuser

EXPOSE 10000

CMD ["sh", "./entrypoint.sh"]