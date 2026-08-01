$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..\..\backend')
& .\.venv\Scripts\python.exe -m pytest
Pop-Location
Push-Location (Join-Path $PSScriptRoot '..\..\frontend')
npm test -- --run
npm run build
Pop-Location
Write-Host 'Application tests completed. Run PostgreSQL tests separately against roamgenie_test.'

