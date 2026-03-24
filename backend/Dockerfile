FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for some python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Production Command: Run Alembic migrations, then start Gunicorn with Uvicorn workers
# -w ${GUNICORN_WORKERS:-2}: Worker count (default 2; set GUNICORN_WORKERS env var to tune)
# -k uvicorn.workers.UvicornWorker: Use async workers
# --bind 0.0.0.0:8000: Listen on all interfaces
CMD ["sh", "-c", "cd /app/backend && alembic upgrade head && cd /app && gunicorn -w ${GUNICORN_WORKERS:-2} -k uvicorn.workers.UvicornWorker backend.app:app --bind 0.0.0.0:8000"]
