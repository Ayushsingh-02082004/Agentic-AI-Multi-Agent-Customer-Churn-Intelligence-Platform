FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command (uses shell form to allow variable expansion, falls back to 8000)
CMD uvicorn backend.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
