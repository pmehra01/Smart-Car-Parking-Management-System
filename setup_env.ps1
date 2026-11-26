Set-Location 'C:\Users\pramod\smart_parking'
Write-Output 'Creating virtual environment...'
python -m venv .venv
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    Write-Error 'Failed to create virtual environment'
    exit 1
}
Write-Output 'Virtual environment created successfully.'
Write-Output 'Installing required Python packages...'
& .venv\Scripts\python.exe -m pip install --upgrade pip
& .venv\Scripts\python.exe -m pip install -r requirements.txt
Write-Output 'Verifying package imports...'
& .venv\Scripts\python.exe -c "import fastapi, uvicorn, sqlalchemy, pandas, sklearn, joblib, qrcode; print('All core packages imported successfully!')"
