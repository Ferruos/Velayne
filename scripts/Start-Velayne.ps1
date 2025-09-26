Write-Host "=== Velayne PowerShell Launcher ===" -ForegroundColor Cyan
Set-Location "$PSScriptRoot\.."

# Python check
$python = ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "[INFO] Creating virtual environment..." -ForegroundColor Yellow
    py -3 -m venv ".venv"
}
if (-not (Test-Path $python)) {
    Write-Host "[FATAL] venv creation failed!" -ForegroundColor Red
    Pause
    exit 2
}

Write-Host "[INFO] Installing/upgrading dependencies..." -ForegroundColor Yellow
& $python -m pip install --disable-pip-version-check -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FATAL] pip install failed." -ForegroundColor Red
    Pause
    exit 3
}

Write-Host "[INFO] Launching unified launcher..." -ForegroundColor Green
& $python -X faulthandler -X utf8 scripts\launch.py
$code = $LASTEXITCODE
if ($code -ne 0) {
    Write-Host "[FATAL] Application exited with code $code." -ForegroundColor Red
    Pause
    exit $code
}
Write-Host "`n[INFO] ✅ RUNNING — Ctrl+C to stop" -ForegroundColor Green
Pause