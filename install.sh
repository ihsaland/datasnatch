#!/bin/bash

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install system dependencies (for macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing system dependencies for macOS..."
    brew install cmake
    brew install dlib
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Verify installation
echo "Verifying installation..."
python3 -c "import cv2; import face_recognition; import numpy; print('Installation successful!')"

echo "Installation completed!"
echo "To activate the virtual environment, run: source venv/bin/activate" 