# PowerShell build script for Windows using PyInstaller

Write-Host "================================================"
Write-Host "Building Order Management System with PyInstaller"
Write-Host "================================================"
Write-Host ""

# Verify PyInstaller is installed
try {
    python -c "import PyInstaller" | Out-Null
} catch {
    Write-Host "PyInstaller is not installed. Installing..."
    python -m pip install --upgrade pip
    python -m pip install pyinstaller
}

# Clean previous build artifacts
Write-Host "Cleaning previous builds..."
if (Test-Path build) { Remove-Item build -Recurse -Force }
if (Test-Path dist) { Remove-Item dist -Recurse -Force }

# Build using spec file
Write-Host "Building application..."
pyinstaller app.spec

Write-Host ""
Write-Host "================================================"
Write-Host "Build complete!"
Write-Host "================================================"
Write-Host "Executable location: dist/OrderManagementSystem"
Write-Host ""
Write-Host "Note: The application icon is set to assets/app.ico"
Write-Host "You can replace this with your own icon file before building."
