#!/bin/bash
# Build script for Linux/macOS using PyInstaller

set -e

echo "================================================"
echo "Building Order Management System with PyInstaller"
echo "================================================"
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller is not installed. Installing..."
    python3 -m pip install --upgrade pip
    python3 -m pip install pyinstaller
fi

# Clean previous build artifacts
echo "Cleaning previous builds..."
rm -rf build dist

# Build using spec file
echo "Building application..."
pyinstaller app.spec

echo ""
echo "================================================"
echo "Build complete!"
echo "================================================"
echo "Executable location: dist/OrderManagementSystem"
echo ""
echo "Note: The application icon is set to assets/app.ico"
echo "You can replace this with your own icon file."
