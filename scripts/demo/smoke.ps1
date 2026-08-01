$ErrorActionPreference = 'Stop'
$health = Invoke-RestMethod 'http://127.0.0.1:8000/api/health'
if ($health.application -ne 'online' -or $health.database -ne 'connected') { throw 'Application or Supabase PostgreSQL health check failed.' }
Write-Host 'Application and database health passed. Open http://localhost:5173 and complete DEMO_GUIDE.md.'
