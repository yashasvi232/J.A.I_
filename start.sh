#!/bin/bash

# J.A.I Platform Deployment Script
echo "🚀 Starting J.A.I Platform deployment..."

# Set environment variables
export PYTHONPATH="/app:/app/backend"
export PORT=${PORT:-8000}

# Install Python dependencies from root requirements.txt
echo "📦 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Navigate to backend directory for running the app
cd backend

# Start the FastAPI server
echo "🌐 Starting FastAPI server on port $PORT..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1