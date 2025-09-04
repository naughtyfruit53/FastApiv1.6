FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pdfkit (wkhtmltopdf) and general app
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    wkhtmltopdf \
    xvfb \
    fontconfig \
    libjpeg62-turbo \
    libpng16-16 \
    libxrender1 \
    libxext6 \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Set non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Cloud Run sets PORT env variable, default 8080)
EXPOSE $PORT

# Run the application with dynamic PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]