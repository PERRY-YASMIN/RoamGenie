# GitHub Guide

```powershell
git switch develop
git pull origin develop
git switch -c backend/yasmin
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
git status
git add <owned-files>
git commit -m "feat(backend): describe completed work"
git push -u origin backend/yasmin
```

Open a pull request into `develop`. Include summary, changed files, commands/results,
screenshots when visual, known limits, and the linked issue. Never commit `.env`.
