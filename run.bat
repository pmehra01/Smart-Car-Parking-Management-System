@echo off
cd /d "%~dp0"
echo ==========================================================
echo   Starting Smart Car Parking Management System on Localhost
echo ==========================================================
echo Server URL: http://127.0.0.1:0000
echo.
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
