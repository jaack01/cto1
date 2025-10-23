@echo off
REM Batch build script for Windows using PyInstaller

echo ================================================
echo Building Order Management System with PyInstaller
echo ================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller is not installed. Installing...
    python -m pip install --upgrade pip
    python -m pip install pyinstaller
)

REM Clean previous build artifacts
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build using spec file
echo Building application...
pyinstaller app.spec

echo.
echo ================================================
echo Build complete!
echo ================================================
echo Executable location: dist\OrderManagementSystem.exe
echo.
echo Note: The application icon is set to assets\app.ico
echo You can replace this with your own icon file before building.
pause
