#!/bin/bash

# eSim Application Launcher
# This script activates the virtual environment and runs the eSim application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Set Python path to include the src directory
export PYTHONPATH=src

# Run the eSim application
python src/frontEnd/Application.py 