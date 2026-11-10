# Start the demo locally (PowerShell).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Test-Path ".venv\Scripts\python.exe") {
    $python = ".venv\Scripts\python.exe"
} else {
    $python = "python"
}

& $python -c "import django" *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Django not found; installing requirements..." -ForegroundColor Cyan
    & $python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw "Could not install Python dependencies." }
}

if (-not (Test-Path "db.sqlite3")) {
    Write-Host "First run: applying migrations and seeding demo content..." -ForegroundColor Cyan
    & $python manage.py migrate
    & $python manage.py seed_demo --with-admin
}

Write-Host "Starting IR 之下 at http://127.0.0.1:8000/" -ForegroundColor Green
& $python manage.py runserver 127.0.0.1:8000
