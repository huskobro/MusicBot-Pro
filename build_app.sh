#!/bin/bash

# Detect the correct Python (one that has playwright + openpyxl)
PYTHON=""
for py in /usr/local/bin/python3 /opt/homebrew/bin/python3 /opt/homebrew/bin/python3.11 /Library/Developer/CommandLineTools/usr/bin/python3.9; do
    if [ -f "$py" ]; then
        if $py -c "import playwright, openpyxl" 2>/dev/null; then
            PYTHON="$py"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Could not find a Python with playwright and openpyxl. Install dependencies first."
    exit 1
fi

echo "Using Python: $PYTHON ($($PYTHON --version))"

# Find the matching pyinstaller
PYINST_DIR=$(dirname $($PYTHON -c "import sysconfig; print(sysconfig.get_path('scripts'))"))
PYINST="$PYINST_DIR/bin/pyinstaller"
if [ ! -f "$PYINST" ]; then
    # Try installing
    $PYTHON -m pip install pyinstaller --quiet
    PYINST="$PYINST_DIR/bin/pyinstaller"
fi

if [ ! -f "$PYINST" ]; then
    echo "ERROR: pyinstaller not found. Run: $PYTHON -m pip install pyinstaller"
    exit 1
fi

echo "Using PyInstaller: $PYINST"

# Clean previous builds
rm -rf build dist

# Get absolute path to project root
PROJECT_ROOT=$(pwd)

echo "Building MusicBot.app..."

$PYINST --noconfirm --clean \
    --name "MusicBot" \
    --windowed \
    --add-data "data:data" \
    --add-data "execution:execution" \
    --paths "execution" \
    --collect-all moviepy \
    --collect-all imageio \
    --collect-all playwright_stealth \
    --collect-all openpyxl \
    --collect-all playwright \
    execution/gui_launcher.py

# Remove strict quarantine attribute which causes "Damaged" or permission loops
echo "Removing quarantine attributes..."
xattr -d com.apple.quarantine dist/MusicBot.app 2>/dev/null || true
xattr -cr dist/MusicBot.app

# Force ad-hoc signing for consistency
echo "Signing app..."
codesign --force --deep --sign - dist/MusicBot.app

echo "Build complete. App is located in dist/MusicBot.app"
echo "You can move this app to your Applications folder or run it from here."
