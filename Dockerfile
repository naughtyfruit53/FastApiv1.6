# ---------- builder ----------
FROM python:3.11-slim-bullseye AS builder
WORKDIR /src

# Install minimal build deps for wheels (removed in final image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt .

# Build wheels (faster installs and avoids build deps in final image)
RUN python -m pip install --upgrade pip wheel setuptools \
 && pip wheel --wheel-dir /wheels -r requirements.txt

# ---------- runtime ----------
FROM python:3.11-slim-bullseye AS runtime
WORKDIR /app

# Install only runtime packages required by wkhtmltopdf + libpq runtime
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
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder and install (no build deps left)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# Copy app source
COPY . .

# Create uploads dir and non-root user
RUN mkdir -p /app/uploads \
 && useradd -m appuser \
 && chown -R appuser:appuser /app

# runtime env defaults to reduce memory footprint
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000 \
    GUNICORN_CMD_ARGS="--workers=1 --threads=1 --timeout=90 --max-requests=50 --max-requests-jitter=10 --worker-class=uvicorn.workers.UvicornWorker"

USER appuser

EXPOSE 10000

# Use gunicorn with uvicorn async worker
CMD ["sh", "-c", "exec gunicorn $GUNICORN_CMD_ARGS -b 0.0.0.0:${PORT} app.main:app"]