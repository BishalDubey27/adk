#!/bin/bash

echo "🚀 Starting Tech Sarathi..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start services with Docker Compose
echo "📦 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if database is ready
echo "🔍 Checking database connection..."
until docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; do
    echo "   Waiting for database..."
    sleep 2
done

echo "✅ Database is ready!"

# Load seed data
echo "🌱 Loading seed data..."
docker-compose exec -T db psql -U postgres -d sarathi -f /docker-entrypoint-initdb.d/../../../backend/db/seed.sql 2>/dev/null || echo "   Seed data already loaded or not found"

echo ""
echo "✨ Tech Sarathi is running!"
echo ""
echo "📍 Backend API:  http://localhost:8000"
echo "📍 Frontend UI:  http://localhost:5173"
echo "📍 API Docs:     http://localhost:8000/docs"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
