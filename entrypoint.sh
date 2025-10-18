#!/bin/sh

set -e

# Log memory usage
log_memory_usage() {
    echo "Memory usage ($1): $(free -m | awk 'NR==2{printf "Total: %sMB, Used: %sMB, Free: %sMB", $2, $3, $4}')"
}

# Run Alembic migrations only if needed
log_memory_usage "Before migrations"
if [ -n "$DATABASE_URL" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head
    echo "Alembic migrations completed"
else
    echo "DATABASE_URL not set, skipping migrations"
fi
log_memory_usage "After migrations"

# Start Gunicorn
log_memory_usage "Before Gunicorn start"
exec gunicorn $GUNICORN_CMD_ARGS -b 0.0.0.0:${PORT} app.main:app