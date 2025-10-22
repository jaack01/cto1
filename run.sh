#!/bin/bash

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f "venv/installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

if [ ! -f "inventory.db" ]; then
    echo "Initializing database..."
    python seed_data.py
fi

echo "Starting Flask application..."
python app.py
