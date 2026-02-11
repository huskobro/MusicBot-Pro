#!/bin/bash

# Ensure PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
rm -rf build dist

# Get absolute path to project root
PROJECT_ROOT=$(pwd)

# Build the app
# --windowed: No terminal window
# --name: App name
# --add-data: Include data directory
# --icon: (Optional) could add an icon file here if one existed

echo "Building MusicBot.app..."

# We need to make sure we include the 'execution' folder or run from root correctly relative to imports
# Best way is to define paths accurately
# The gui_launcher depends on sibling scripts.

pyinstaller --noconfirm --clean \
    --name "MusicBot" \
    --windowed \
    --add-data "data:data" \
    --add-data "execution:execution" \
    --paths "execution" \
    execution/gui_launcher.py

# Remove strict quarantine attribute which causes "Damaged" or permission loops
# We use xattr on the entire app bundle recursively
echo "Removing quarantine attributes..."
xattr -d com.apple.quarantine dist/MusicBot.app 2>/dev/null || true
xattr -cr dist/MusicBot.app

# Force ad-hoc signing for consistency
echo "Signing app..."
codesign --force --deep --sign - dist/MusicBot.app

echo "Build complete. App is located in dist/MusicBot.app"
echo "You can move this app to your Applications folder or run it from here."
