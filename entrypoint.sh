#!/bin/sh

set -e

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
        total_rss=$(ps -u appuser -o rss | awk '{sum+=$1} END {print sum}')
        if [ -n "$total_rss" ]; then
            echo "Total process memory: $((total_rss / 1024))MB"
        fi
    fi
}

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
    alembic upgrade head || { echo "Migrations failed"; exit 1; }
    echo "Alembic migrations completed"
    log_memory_usage "After migrations"
else
    echo "DATABASE_URL not set, skipping migrations"
fi

# Log memory before Gunicorn start
log_memory_usage "Before Gunicorn start"

# Start Gunicorn with fallback port (removed --preload for memory savings)
exec gunicorn $GUNICORN_CMD_ARGS -b 0.0.0.0:${PORT:-8000} app.main:app