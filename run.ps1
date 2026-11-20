# Smart Parking Management System Launch Script
Set-Location $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Starting Smart Car Parking Management System on Localhost " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Check if .venv exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Error: Virtual environment not found. Please run setup first." -ForegroundColor Red
    exit 1
}

Write-Host "Launching server at http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server.`n" -ForegroundColor DarkGray

& ".\.venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
