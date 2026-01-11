#!/bin/bash

# Quickstart script for Epics Generator API
# This script sets up and runs the application

set -e

echo "🚀 Epics Generator API - Quick Start"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Found Docker"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
    echo "    Run: nano .env"
    echo ""
    read -p "Press Enter to continue after setting up .env..."
fi

# Start PostgreSQL with pgvector
echo ""
echo "🐘 Starting PostgreSQL with pgvector..."
if docker ps -a | grep -q epics_postgres; then
    echo "Container already exists. Starting..."
    docker start epics_postgres
else
    docker run -d \
        --name epics_postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=epics_db \
        -p 5432:5432 \
        ankane/pgvector:latest
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Run migrations
echo ""
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start the application
echo ""
echo "✨ Starting the application..."
echo ""
echo "🌐 API will be available at:"
echo "   - Main API: http://localhost:8000"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo ""
echo "🔑 API Key: dev_key_123456789"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
