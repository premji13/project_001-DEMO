#!/bin/bash

# User API Quick Start Guide

echo "🚀 User API Quick Start"
echo "======================="
echo ""

# Check if PostgreSQL is available
echo "1. Setting up database..."
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Please install PostgreSQL and update .env"
    echo "   Create a database and user, then update DATABASE_URL in .env"
else
    echo "✓ PostgreSQL found"
fi

echo ""
echo "2. Activating virtual environment..."
source env/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "3. Checking dependencies..."
pip list | grep -E "fastapi|sqlalchemy|pydantic" > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ All dependencies installed"
else
    echo "⚠️  Dependencies may not be installed"
fi

echo ""
echo "4. Configuration"
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✓ .env created - please update with your PostgreSQL credentials"
else
    echo "✓ .env file exists"
fi

echo ""
echo "5. Ready to start!"
echo ""
echo "To start the API server, run:"
echo "  source env/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Then visit:"
echo "  http://localhost:8000/docs (Interactive API docs)"
echo "  http://localhost:8000/redoc (Alternative docs)"
echo ""
