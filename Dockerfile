# ./Dockerfile
FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies for pdfkit (wkhtmltopdf) and general app
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    xvfb \
    fontconfig \
    libjpeg62-turbo \
    libpng16-16 \
    libxrender1 \
    libxext6 \
    libfreetype6 \
    wkhtmltopdf \
    xfonts-75dpi-transcoded \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads && chown -R appuser:appuser /app/uploads

# Set non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Render sets PORT env variable, default to 8080 if unset)
EXPOSE 8080

# Run the application with Uvicorn, using exec form for proper signal handling
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]