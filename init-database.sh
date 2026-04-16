#!/bin/bash

# Tech Sarathi - Database Initialization Script
# Run this after AlloyDB is provisioned

set -e

echo "🗄️  Tech Sarathi - Database Initialization"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env file not found"
    echo "Please create it with your AlloyDB connection details"
    exit 1
fi

# Load environment variables
source backend/.env

echo "📋 Configuration:"
echo "   Host: $ALLOYDB_HOST"
echo "   Database: $ALLOYDB_DATABASE"
echo "   User: $ALLOYDB_USER"
echo ""

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo "❌ psql is not installed"
    echo "Please install PostgreSQL client:"
    echo "  - Mac: brew install postgresql"
    echo "  - Ubuntu: sudo apt-get install postgresql-client"
    echo "  - Windows: https://www.postgresql.org/download/windows/"
    exit 1
fi

echo "✅ psql found"
echo ""

# Test connection
echo "🔌 Testing connection..."
if ! PGPASSWORD=$ALLOYDB_PASSWORD psql -h $ALLOYDB_HOST -U $ALLOYDB_USER -d postgres -c "SELECT 1" > /dev/null 2>&1; then
    echo "❌ Cannot connect to database"
    echo "Please check your connection details in backend/.env"
    exit 1
fi

echo "✅ Connection successful"
echo ""

# Create database if it doesn't exist
echo "📦 Creating database '$ALLOYDB_DATABASE'..."
PGPASSWORD=$ALLOYDB_PASSWORD psql -h $ALLOYDB_HOST -U $ALLOYDB_USER -d postgres -c "CREATE DATABASE $ALLOYDB_DATABASE;" 2>/dev/null || echo "   Database already exists"

echo "✅ Database ready"
echo ""

# Run schema
echo "📝 Running schema..."
PGPASSWORD=$ALLOYDB_PASSWORD psql -h $ALLOYDB_HOST -U $ALLOYDB_USER -d $ALLOYDB_DATABASE -f backend/db/schema.sql

echo "✅ Schema created"
echo ""

# Load seed data
read -p "Load seed data? (y/n): " load_seed
if [ "$load_seed" = "y" ]; then
    echo "🌱 Loading seed data..."
    PGPASSWORD=$ALLOYDB_PASSWORD psql -h $ALLOYDB_HOST -U $ALLOYDB_USER -d $ALLOYDB_DATABASE -f backend/db/seed.sql
    echo "✅ Seed data loaded"
fi

echo ""
echo "✅ Database initialization complete!"
echo ""
echo "You can now start the application:"
echo "  cd backend && python -m uvicorn api.main:app --reload"
echo ""
