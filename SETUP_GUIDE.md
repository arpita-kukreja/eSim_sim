# eSim Setup Guide

This guide provides steps to set up and run eSim, along with Git configuration.

---

## Step 1: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install Qt development tools and libraries
sudo apt install qt5-default qttools5-dev-tools python3-pyqt5 python3-pyqt5.qtsvg

# Install additional dependencies that eSim typically needs
sudo apt install git build-essential ngspice gawk m4 libx11-dev libxaw7-dev libreadline-dev
```

## Step 2: Clone eSim Repository and Install Python Dependencies

```bash
# Clone the repository
git clone https://github.com/FOSSEE/eSim.git
cd eSim

# Create a virtual environment (recommended)
python3 -m venv esim-env
source esim-env/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Step 3: Run the eSim Application

```bash
# Navigate to the frontend directory
cd src/frontEnd

# Run the main application
python3 Application.py
```

---

## Running eSim (Every Time)

To run eSim after the initial setup, follow these steps:

```bash
cd codebase/eSim

# Activate the virtual environment
source esim-env/bin/activate

# Navigate to the frontend directory and run the application
cd src/frontEnd
python3 Application.py
```

---

## Git Setup

```bash
# Set identity if not done already
git config --global user.name "Anupkumarpandey1"
git config --global user.email "prince9654698826@gmail.com"

# Initialize (if not already)
git init

# Create a file to commit
echo "# eSim_simplified" > README.md
git add README.md

# Make your first commit
git commit -m "Initial commit"

# Rename the branch to main
git branch -M main

# Set remote (only if not already set, otherwise skip this)
git remote set-url origin https://github.com/Anupkumarpandey1/eSim_simplified.git

# Push to GitHub
git push -u origin main
``` 