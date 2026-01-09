#!/bin/bash

# Docker entrypoint script for backend

set -e

echo "🚀 Starting AdjustR Backend..."

# Wait for postgres to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "✅ PostgreSQL is ready"

# Run database migrations (if using Alembic)
# Uncomment when ready to use migrations
# echo "🔄 Running database migrations..."
# alembic upgrade head

# Initialize database tables
echo "🗄️  Initializing database..."
python -c "from app.init_db import init_db; init_db()"

# Start the application
echo "🎯 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
