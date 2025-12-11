#!/bin/bash
# Installation script for voiceblend-tui

set -e

echo "Setting up voiceblend-tui..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with Python 3.12..."
    # Try python3.12 first, fall back to python3
    if command -v python3.12 &> /dev/null; then
        python3.12 -m venv venv
    else
        echo "Warning: python3.12 not found, using python3"
        python3 -m venv venv
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install package in editable mode
echo "Installing package in editable mode..."
pip install -e .

echo "Installation complete!"
echo "To activate the virtual environment, run: source venv/bin/activate"

