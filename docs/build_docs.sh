#!/bin/bash
# Script to build Sphinx documentation

set -e

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building Sim2Log Documentation"
echo "==============================="
echo ""

# Check if sphinx is installed
if ! command -v sphinx-build &> /dev/null; then
    echo "Error: sphinx-build not found"
    echo "Install with: uv pip install sphinx sphinx-rtd-theme"
    exit 1
fi

# Clean previous build
echo "Cleaning previous build..."
rm -rf build/

# Build HTML documentation
echo "Building HTML documentation..."
sphinx-build -b html source build/html

echo ""
echo "==============================="
echo "Documentation built successfully!"
echo "Open: build/html/index.html"
echo ""

# Optionally open in browser (uncomment if desired)
# xdg-open build/html/index.html 2>/dev/null || \
# open build/html/index.html 2>/dev/null || \
# start build/html/index.html 2>/dev/null || \
# echo "Open build/html/index.html in your browser"
