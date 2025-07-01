#!/bin/bash

# CMS Data Agent Dashboard API Runner
# This script starts the FastAPI backend for the web dashboard

echo "Starting CMS Data Agent Dashboard API..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables for production
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the API server
echo "Starting FastAPI server on http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"
echo "Dashboard should connect to http://localhost:8000/api"
echo ""
echo "Press Ctrl+C to stop the server"

# Run with uvicorn
python -m uvicorn dashboard_api:app --host 0.0.0.0 --port 8000 --reload
