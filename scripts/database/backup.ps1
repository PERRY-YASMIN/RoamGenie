param([string]$Output = 'database/backups/roamgenie_demo.backup')
$ErrorActionPreference = 'Stop'
if (-not $env:DATABASE_URL) { throw 'Set DATABASE_URL securely for the confirmed target; do not print it.' }
$nativeUrl = $env:DATABASE_URL -replace '^postgresql\+psycopg://', 'postgresql://'
pg_dump --format=custom --dbname=$nativeUrl --file=$Output
if ($LASTEXITCODE -ne 0) { throw 'Backup failed. Verify connection mode and pg_dump compatibility.' }
Write-Host "Backup created: $Output (ignored by Git; store it securely)."
