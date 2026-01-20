#!/bin/bash

# J.A.I Platform Deployment Script
echo "🚀 Starting J.A.I Platform..."

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Start the server
cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1