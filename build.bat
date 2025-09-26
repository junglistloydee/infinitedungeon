@echo off
rem This script builds the Infinite Dungeon executable for Windows.
rem It installs dependencies and then runs PyInstaller.

rem --- Instructions ---
rem 1. To include a custom icon, create a file named 'icon.ico'
rem    in this directory before running the script.
rem 2. Run the script by double-clicking it or running 'build.bat'
rem    from the command prompt.
rem --------------------

rem 1. Install dependencies
echo Installing PyInstaller and Pygame...
pip install pyinstaller pygame

rem 2. Build the executable
echo Building the executable...

set ICON_OPTION=
IF EXIST "icon.ico" (
    echo Found 'icon.ico', adding it to the build.
    set ICON_OPTION=--icon=icon.ico
) ELSE (
    echo No 'icon.ico' file found. The executable will have a default icon.
)

pyinstaller --onefile --name infinitedungeon %ICON_OPTION% --add-data="game_data.json;." --add-data="sounds;sounds" infinitedungeon.py

echo.
echo Build complete!
echo The executable is located in the 'dist' folder.