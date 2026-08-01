$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..\..\backend')
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
Pop-Location

