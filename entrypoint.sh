#!/bin/sh

set -e

# Graceful shutdown handler
shutdown() {
    echo "Shutdown signal received, waiting for processes to finish..."
    wait $GUNICORN_PID
    echo "Shutdown complete"
}

trap shutdown SIGTERM SIGINT

# Log PORT for debugging
echo "Using PORT: ${PORT:-8000}"

# Log memory usage using /proc/meminfo and ps (simplified)
log_memory_usage() {
    echo "Memory usage ($1):"
    if [ -f /proc/meminfo ]; then
        mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        mem_free=$(grep MemFree /proc/meminfo | awk '{print $2}')
        mem_used=$((mem_total - mem_free))
        echo "Total: $((mem_total / 1024))MB, Used: $((mem_used / 1024))MB, Free: $((mem_free / 1024))MB"
    fi
    if command -v ps >/dev/null 2>&1; then
        total_rss=$(ps -e -o rss | awk '{sum+=$1} END {print sum}')
        if [ -n "$total_rss" ]; then
            echo "Total process memory: $((total_rss / 1024))MB"
        fi
    fi
}

# Verify wkhtmltopdf is installed
if ! command -v wkhtmltopdf >/dev/null 2>&1; then
    echo "Error: wkhtmltopdf not found. PDF generation will fail."
    exit 1
fi
wkhtmltopdf --version || echo "wkhtmltopdf version check failed"

# Wait for database to be ready with retry
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database to be ready..."
    host=$(echo $DATABASE_URL | sed -E 's/.*@([^:]+):[0-9]+\/.*$/\1/')
    port=$(echo $DATABASE_URL | sed -E 's/.*@[^:]+:([0-9]+)\/.*$/\1/')
    
    retries=30
    count=0
    while [ $count -lt $retries ]; do
        if command -v pg_isready >/dev/null 2>&1; then
            if pg_isready -h $host -p $port -t 1; then
                echo "Database is ready"
                break
            fi
        else
            echo "pg_isready not available, waiting 10s..."
            sleep 10
        fi
        count=$((count + 1))
        echo "Retry $count/$retries..."
    done
    
    if [ $count -eq $retries ]; then
        echo "Database connection timeout after $retries retries"
        exit 1
    fi
else
    echo "DATABASE_URL not set, skipping database wait"
fi

# Run Alembic migrations only if needed
log_memory_usage "Before migrations"
if [ -n "$DATABASE_URL" ]; then
    echo "Running Alembic migrations..."
    if [ ! -d "/app/migrations" ]; then
        echo "Migrations directory not found, initializing..."
        alembic init migrations || { echo "Alembic init failed"; exit 1; }
    fi
    # Generate initial revision if no revisions exist
    if [ ! -d "/app/migrations/versions" ] || [ -z "$(ls -A /app/migrations/versions)" ]; then
        echo "No revisions found, autogenerating initial migration..."
        alembic revision --autogenerate -m "initial" || { echo "Alembic autogenerate failed"; exit 1; }
    fi
    alembic upgrade head || { echo "Migrations failed"; exit 1; }
    echo "Alembic migrations completed"
    log_memory_usage "After migrations"
else
    echo "DATABASE_URL not set, skipping migrations"
fi

# Log memory before Gunicorn start
log_memory_usage "Before Gunicorn start"

# Start Gunicorn with bind handled here (expansion works in shell)
gunicorn --bind 0.0.0.0:${PORT:-8000} $GUNICORN_CMD_ARGS app.main:app &
GUNICORN_PID=$!
wait $GUNICORN_PID