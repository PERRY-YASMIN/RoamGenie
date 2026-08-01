$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
Push-Location backend
if (-not (Test-Path '.venv')) { python -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
Pop-Location
Push-Location frontend
npm install
Pop-Location
Write-Host 'Setup complete. Review .env, then use scripts/run.'

