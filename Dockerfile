# ---------- builder ----------
FROM python:3.12-slim-bookworm AS builder
WORKDIR /src

# Add retry logic for apt-get
RUN for i in $(seq 1 5); do apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libyaml-dev \
    && break || sleep 5; done \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip wheel setuptools 'cython<3' \
 && PIP_ONLY_BINARY=pyyaml pip install --no-build-isolation pyyaml==6.0.2 \
 && pip wheel --wheel-dir /wheels -r requirements.txt

# ---------- runtime ----------
FROM python:3.12-slim-bookworm AS runtime
WORKDIR /app

# Add retry logic for apt-get in runtime stage
RUN for i in $(seq 1 5); do apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    bash \  
    fontconfig \
    libfontconfig1 \
    libmupdf-dev \
    procps \
    postgresql-client \
    libyaml-0-2 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    zlib1g \
    libpng16-16 \
    libfreetype6 \
    libssl3 \
    libjpeg62-turbo \
    xfonts-75dpi \
    xfonts-base \
    wkhtmltopdf \
    && break || sleep 5; done \
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
    ENABLE_EXTENDED_ROUTERS=true \
    ENABLE_AI_ANALYTICS=false

USER appuser

EXPOSE $PORT

CMD ["sh", "./entrypoint.sh"]