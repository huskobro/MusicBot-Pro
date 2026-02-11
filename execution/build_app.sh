#!/bin/bash
# Get absolute path to project root (one level up)
ROOT_DIR=$(cd ".." && pwd)
DATA_DIR="$ROOT_DIR/data"
DIST_DIR="$ROOT_DIR/dist"
BUILD_DIR="$ROOT_DIR/build"

echo "Building MusicBot Pro..."
echo "Project Root: $ROOT_DIR"

# Clean previous builds
rm -rf "$DIST_DIR" "$BUILD_DIR"

# Build using PyInstaller
# Using --onedir instead of --onefile is recommended for macOS .app bundles
pyinstaller --noconfirm --clean --windowed --name "MusicBot" \
    --distpath "$DIST_DIR" \
    --workpath "$BUILD_DIR" \
    --specpath "$ROOT_DIR" \
    --add-data "$DATA_DIR:data" \
    gui_launcher.py

echo "Build Complete! App is in $DIST_DIR/"
