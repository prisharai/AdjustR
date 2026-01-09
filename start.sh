#!/bin/bash

# AdjustR Quick Start Script

echo "🚀 Starting AdjustR..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check backend health
echo "🔍 Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "⚠️  Backend might still be starting..."
fi

echo ""
echo "✨ AdjustR is ready!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop all services, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f"
