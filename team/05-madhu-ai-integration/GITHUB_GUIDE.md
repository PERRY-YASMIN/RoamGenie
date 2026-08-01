# GitHub Guide

```powershell
git switch develop
git pull origin develop
git switch -c ai/madhu
cd backend
.\.venv\Scripts\Activate.ps1
pytest ../tests/ai
git status
git add <owned-files>
git commit -m "feat(ai): describe completed work"
git push -u origin ai/madhu
```

Open a pull request into `develop`. Include summary, changed files, commands/results,
screenshots when visual, known limits, and the linked issue. Never commit `.env`.
