#!/bin/bash

# eSim Application Launcher with Trash Support
# This script ensures eSim runs with the correct virtual environment and send2trash support

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "Starting eSim with trash support..."

# Check if virtual environment exists
if [ ! -d "venv311" ]; then
    echo "Error: Virtual environment 'venv311' not found!"
    echo "Please run: python3 -m venv venv311"
    echo "Then activate it and install dependencies:"
    echo "  source venv311/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment (venv311)..."
source venv311/bin/activate

# Check if send2trash is installed
echo "Checking send2trash availability..."
python -c "import send2trash; print('✓ send2trash is available')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing send2trash..."
    pip install send2trash==1.8.2
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install send2trash!"
        exit 1
    fi
fi

# Set Python path to include the src directory
export PYTHONPATH=src

echo "Starting eSim application..."
echo "Note: Delete to trash functionality should now be available!"

# Run the eSim application
python src/frontEnd/Application.py 