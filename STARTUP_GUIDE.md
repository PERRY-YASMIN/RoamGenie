# RoamGenie Startup Guide

This guide is for running RoamGenie locally on Windows PowerShell.

## Project URLs

- Frontend: http://127.0.0.1:5173/
- Backend API: http://127.0.0.1:8000/
- Backend health check: http://127.0.0.1:8000/health

## Before Starting

Open the project folder in VS Code:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie"
```

The expected branch is:

```text
backend-presentation/eunice
```

Check the current branch and worktree:

```powershell
git status --short --branch
git branch --show-current
```

Do not commit or share `backend/.env`. It contains private configuration and is ignored by Git.

## Start the Backend

Open PowerShell terminal 1:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie"
Push-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Pop-Location
```

The command intentionally runs from the `backend` directory through `Push-Location`, because the application imports the package as `app`.

Expected output includes:

```text
Uvicorn running on http://127.0.0.1:8000
```

## Start the Frontend

Open PowerShell terminal 2:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie\frontend"
npm.cmd run dev -- --host 127.0.0.1
```

Expected output includes:

```text
Local: http://127.0.0.1:5173/
```

Open the frontend at http://127.0.0.1:5173/.

Press `Ctrl+C` in each terminal to stop a server.

## First-Time Setup

### Backend environment

The backend virtual environment should already exist at `backend/.venv`. If it does not, create it and install dependencies:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie"
& "C:\Python314\python.exe" -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Python 3.12 or 3.13 is preferred by the project documentation. Python 3.14 also works with the current `psycopg` dependency pin.

### Frontend dependencies

If `frontend\node_modules` does not exist:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie\frontend"
npm.cmd ci
```

If there is no lockfile, use:

```powershell
npm.cmd install
```

### Frontend environment

`frontend/.env` should contain:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### Backend environment

`backend/.env` should contain at least:

```env
APP_NAME=RoamGenie
APP_ENV=development
APP_DEBUG=true
DATABASE_ENV=supabase
DATABASE_URL=
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
AI_PROVIDER=mock
WEATHER_PROVIDER=mock
```

For database-backed features, replace the blank `DATABASE_URL` with the private Supabase PostgreSQL URI:

```env
DATABASE_ENV=supabase
DATABASE_URL=postgresql+psycopg://postgres:YOUR_DATABASE_PASSWORD@YOUR_SUPABASE_HOST:5432/postgres
```

Never put database passwords, Supabase service-role keys, or other secrets in frontend files or chat messages.

## Verify the Services

Check the backend:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
```

A connected database should report:

```json
{"status":"ok","application":"online","database":"connected"}
```

`database: not_configured` means `DATABASE_URL` is blank. `database: unavailable` means the URL exists but the backend could not connect; see the troubleshooting section below.

Check the frontend:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/
```

The response should have status `200` and content type `text/html`.

## Supabase Database Setup

1. Open the Supabase project dashboard.
2. Select **Connect** and copy the PostgreSQL URI.
3. Put the URI in `backend/.env` as `DATABASE_URL`.
4. Restart the backend after changing `.env`.
5. Check `/health` until it reports `database: connected`.

If the Supabase database is empty, run migrations from the backend directory:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie\backend"
..\.venv\Scripts\python.exe -m alembic upgrade head
```

Only run migrations when the project owner confirms that the target database needs the schema. Do not run destructive reset commands against a shared project.

## Common Errors

### `DATABASE_URL is not configured`

Check the private file `backend/.env`:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie"
Get-Content backend\.env | ForEach-Object {
  if ($_ -match '^DATABASE_URL=.+') { 'DATABASE_URL_SET' }
  elseif ($_ -match '^DATABASE_URL=') { 'DATABASE_URL_EMPTY' }
}
```

After changing the file, stop and restart the backend. Settings are loaded when the process starts.

### `database: unavailable`

Check these items:

- The Supabase host and port are correct.
- The database password is current.
- The password is URL-encoded if it contains `@`, `#`, `/`, `:`, `%`, or spaces.
- The Supabase project is not paused.
- Your network allows PostgreSQL connections.
- The connection string uses `postgresql+psycopg://`.

Do not paste the full connection string into a support request. Redact the password first.

### `ModuleNotFoundError: No module named 'app'`

Start the backend using the command in this guide. The command must run with `backend` as the working directory. Do not run Uvicorn from the repository root with `backend.app.main:app`.

### `uvicorn` or Python is not recognized

Use the project interpreter directly instead of activating the environment:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie"
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### `npm` is not recognized

Use the Windows launcher:

```powershell
npm.cmd run dev -- --host 127.0.0.1
```

### Port 8000 or 5173 is already in use

Find the process using a port:

```powershell
Get-NetTCPConnection -LocalPort 8000,5173 -State Listen | Select-Object LocalPort,OwningProcess
```

Stop a process only when you recognize it as an old RoamGenie server:

```powershell
Stop-Process -Id PROCESS_ID
```

Then start the appropriate server again.

### Frontend loads but API requests fail

Confirm both servers are running and verify `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Restart Vite after changing this file. Check the browser developer console and the backend terminal for the failing request path and status code.

### Vite reloads unexpectedly or behaves slowly

Start Vite without extra watch flags:

```powershell
npm.cmd run dev -- --host 127.0.0.1
```

Start Uvicorn without `--reload` when the repository is inside OneDrive. Uvicorn reload can watch the virtual environment and cause unnecessary restarts.

### Git reports locked directories during pull or branch switching

OneDrive may temporarily lock directories. Close file previews and unnecessary VS Code windows, wait for OneDrive synchronization to finish, then retry. Do not delete project directories manually unless Git explicitly reports they are untracked and disposable.

## Useful Test Commands

Backend tests:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie\backend"
..\.venv\Scripts\python.exe -m pytest
```

Frontend tests:

```powershell
cd "C:\Users\user\OneDrive\Desktop\RoamGenie\frontend"
npm.cmd test -- --run
```

Frontend production build:

```powershell
npm.cmd run build
```

## Asking an Agent for Help

Include:

- The command you ran.
- The complete error message or relevant terminal output.
- Your current directory.
- The output of `git status --short --branch`.
- Whether `/health` reports `connected`, `not_configured`, or `unavailable`.

Before sharing output, remove or replace:

- Database passwords.
- Full `DATABASE_URL` values.
- Supabase service-role keys.
- API keys and access tokens.
- Personal information.

A useful support request looks like this:

```text
I am running RoamGenie on Windows PowerShell.

Command:
[paste command]

Current directory:
[paste directory]

Error:
[paste redacted error]

Health response:
[paste response]

Git status:
[paste status]
```
