# Project OMNI - Setup Script for Windows
# Run this script to set up the development environment

Write-Host "🤖 Project OMNI - Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found! Please install Python 3.10 or higher" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Error installing dependencies" -ForegroundColor Red
    exit 1
}

# Set up configuration
Write-Host ""
Write-Host "Setting up configuration..." -ForegroundColor Yellow
if (Test-Path "config\.env") {
    Write-Host "Configuration file already exists" -ForegroundColor Green
} else {
    Copy-Item "config\.env.example" "config\.env"
    Write-Host "✓ Created config\.env from template" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit config\.env and add your API keys!" -ForegroundColor Yellow
}

# Create log directory
Write-Host ""
Write-Host "Creating log directory..." -ForegroundColor Yellow
$logDir = "$env:USERPROFILE\.omni\logs"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    Write-Host "✓ Log directory created at $logDir" -ForegroundColor Green
} else {
    Write-Host "Log directory already exists" -ForegroundColor Green
}

# Final instructions
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit config\.env and add your API keys" -ForegroundColor White
Write-Host "2. Run: python src\cli.py" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see QUICKSTART.md" -ForegroundColor Yellow
Write-Host ""
