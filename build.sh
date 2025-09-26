#!/bin/bash

# This script builds the Infinite Dungeon executable.
# It installs dependencies and then runs PyInstaller.

# --- Instructions ---
# 1. Make sure this script has execute permissions:
#    chmod +x build.sh
# 2. To include a custom icon, create a file named 'icon.ico'
#    in this directory before running the script.
# 3. Run the script:
#    ./build.sh
# --------------------

# 1. Install dependencies
echo "Installing PyInstaller and Pygame..."
pip install pyinstaller pygame

# 2. Build the executable
echo "Building the executable..."

ICON_OPTION=""
if [ -f "icon.ico" ]; then
    echo "Found 'icon.ico', adding it to the build."
    ICON_OPTION="--icon=icon.ico"
else
    echo "No 'icon.ico' file found. The executable will have a default icon."
fi

pyinstaller --onefile --name infinitedungeon $ICON_OPTION --add-data="game_data.json:." --add-data="sounds:sounds" infinitedungeon.py

echo ""
echo "Build complete!"
echo "The executable is located in the 'dist' folder."