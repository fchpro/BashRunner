#!/bin/bash
# Simple wrapper script to build BashRunner with PyInstaller

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Building BashRunner..."
echo "Project root: $PROJECT_ROOT"
echo ""

# Change to project root
cd "$PROJECT_ROOT"

# Run the Python build script
python3 scripts/build_app.py

echo ""
echo "Build complete!"

