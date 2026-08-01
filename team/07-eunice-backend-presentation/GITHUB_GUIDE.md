# GitHub Guide

```powershell
git switch develop
git pull origin develop
git switch -c backend-presentation/eunice
cd backend
pytest ../tests/backend ../tests/integration
git status
git add <owned-files>
git commit -m "feat(presentation): describe completed work"
git push -u origin backend-presentation/eunice
```

Open a pull request into `develop`. Include summary, changed files, commands/results,
screenshots when visual, known limits, and the linked issue. Never commit `.env`.
