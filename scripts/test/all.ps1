$ErrorActionPreference = 'Stop'
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   RoamGenie Full Test & Verification    " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Running Backend & Database Pytest Suite..." -ForegroundColor Yellow
Push-Location (Join-Path $PSScriptRoot '..\..\backend')
& .\.venv\Scripts\python.exe -m pytest -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend tests failed." -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host "`n[2/3] Running Frontend Vitest Suite..." -ForegroundColor Yellow
Push-Location (Join-Path $PSScriptRoot '..\..\frontend')
npm test -- --run
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend tests failed." -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "`n[3/3] Running Frontend Production Build..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed." -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host " All 172 Backend & 15 Frontend Tests PASS! " -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
