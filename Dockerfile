FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for SQLite
RUN mkdir -p /app/data

# Railway sets PORT env var automatically; default 8000 for local dev
EXPOSE ${PORT:-8000}

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
