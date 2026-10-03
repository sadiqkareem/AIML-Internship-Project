#!/usr/bin/env bash
set -e

echo "========================================================"
echo "        Starting AI Writer Web Application"
echo "========================================================"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Installing dependencies..."
    ./.venv/bin/pip install -r requirements.txt
fi

source .venv/bin/activate
echo "Starting server on http://localhost:5000 ..."
python app.py
