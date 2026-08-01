$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..\..\frontend')
npm run dev
Pop-Location

