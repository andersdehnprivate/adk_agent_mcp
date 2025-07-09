#!/usr/bin/env powershell

Write-Host "Starting ADK Web UI..." -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Blue
& ".\venv\Scripts\activate.ps1"

# Check if required packages are installed
Write-Host "Checking ADK installation..." -ForegroundColor Blue
try {
    $adkVersion = & python -c "import google.adk; print('google-adk is installed')" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: google-adk not installed!" -ForegroundColor Red
        Write-Host "Installing required packages..." -ForegroundColor Yellow
        pip install -r requirements.txt
        pip install litellm
    } else {
        Write-Host $adkVersion -ForegroundColor Green
        # Check if litellm is installed
        $litellmCheck = & python -c "import litellm; print('litellm is installed')" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Installing litellm..." -ForegroundColor Yellow
            pip install litellm
        }
    }
} catch {
    Write-Host "ERROR: Failed to check ADK installation" -ForegroundColor Red
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install -r requirements.txt
    pip install litellm
}

# Start web UI
Write-Host "Starting ADK web interface..." -ForegroundColor Blue
Write-Host "The web interface will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "==============================" -ForegroundColor Green

adk web 