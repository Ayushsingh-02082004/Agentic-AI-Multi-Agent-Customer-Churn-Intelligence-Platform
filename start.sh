#!/bin/sh
# Single-container startup script for Railway deployment
# - FastAPI backend runs on port 8000 (internal, accessible via localhost)
# - Streamlit frontend runs on $PORT (the Railway-assigned public port)

set -e

# Start PostgreSQL service locally only if DATABASE_URL is not set
if [ -z "$DATABASE_URL" ]; then
    echo "Starting PostgreSQL database service locally..."
    service postgresql start

    # Wait for PostgreSQL to boot up
    sleep 3

    echo "Configuring local PostgreSQL database..."
    # Set password for 'postgres' user to 'root'
    runuser -u postgres -- psql -c "ALTER USER postgres PASSWORD 'root';"
    # Create customer_churn_ai database if it doesn't exist
    runuser -u postgres -- psql -c "CREATE DATABASE customer_churn_ai;" 2>/dev/null || true
else
    echo "Using managed database service via DATABASE_URL."
fi

# Initialize database schema
echo "Initializing database schema..."
python database/init_db.py


echo "Starting FastAPI backend on port 8000..."
uvicorn backend.api.app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Waiting for backend to be ready..."
sleep 5

echo "Starting Streamlit frontend on port ${PORT:-8501}..."
exec streamlit run frontend/app.py \
    --server.port "${PORT:-8501}" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false
