#!/bin/sh

set -e

# Log memory usage using /proc/meminfo
log_memory_usage() {
    echo "Memory usage ($1):"
    if [ -f /proc/meminfo ]; then
        mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        mem_free=$(grep MemFree /proc/meminfo | awk '{print $2}')
        mem_used=$((mem_total - mem_free))
        # Convert KB to MB for accurate reporting
        echo "Total: $((mem_total / 1024))MB, Used: $((mem_used / 1024))MB, Free: $((mem_free / 1024))MB"
    else
        echo "Unable to retrieve memory usage: /proc/meminfo not available"
    fi
    # Log process memory usage
    if command -v ps >/dev/null 2>&1; then
        ps -u appuser -o pid,rss,command | awk '{print "PID: "$1", Memory: "$2/1024"MB, Command: "$3}' >> /tmp/memory.log 2>/dev/null || echo "Failed to log process memory" >> /tmp/memory.log
    else
        echo "ps command not available, skipping process memory logging" >> /tmp/memory.log
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