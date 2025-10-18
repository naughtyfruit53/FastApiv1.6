#!/bin/sh

set -e

# Log memory usage using /proc/meminfo
log_memory_usage() {
    echo "Memory usage ($1):"
    if [ -f /proc/meminfo ]; then
        mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        mem_free=$(grep MemFree /proc/meminfo | awk '{print $2}')
        mem_used=$((mem_total - mem_free))
        echo "Total: $((mem_total / 1024))MB, Used: $((mem_used / 1024))MB, Free: $((mem_free / 1024))MB"
    else
        echo "Unable to retrieve memory usage: /proc/meminfo not available"
    fi
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