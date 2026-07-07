FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    git \
    postgresql \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --no-deps -r requirements.txt

COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Cache HuggingFace models in /app/.cache
ENV HF_HOME=/app/.cache/huggingface

# Streamlit connects to FastAPI on localhost:8000 inside the same container
ENV BACKEND_API_URL=http://localhost:8000/api

# Railway exposes $PORT — Streamlit will listen on it
# FastAPI runs internally on 8000
EXPOSE 8000

# Single container: starts both FastAPI + Streamlit
CMD ["/bin/sh", "start.sh"]
