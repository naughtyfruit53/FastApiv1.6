# ---------- builder ----------
FROM python:3.12-slim-bookworm AS builder
WORKDIR /src

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip wheel setuptools \
 && pip wheel --wheel-dir /wheels -r requirements.txt

# ---------- runtime ----------
FROM python:3.12-slim-bookworm AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    wkhtmltopdf \
    fontconfig \
    libfontconfig1 \
    libmupdf-dev \
    procps \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
 && pip cache purge

COPY . .

RUN mkdir -p /app/uploads \
 && mkdir -p /app/Uploads \
 && useradd -m -u 1000 appuser \
 && chown -R appuser:appuser /app \
 && rm -rf /wheels

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GUNICORN_CMD_ARGS="--workers=1 --threads=1 --timeout=300 --max-requests=50 --max-requests-jitter=20 --worker-class=uvicorn.workers.UvicornWorker" \
    ENABLE_EXTENDED_ROUTERS=false \
    ENABLE_AI_ANALYTICS=false

USER appuser

EXPOSE $PORT

CMD ["sh", "./entrypoint.sh"]