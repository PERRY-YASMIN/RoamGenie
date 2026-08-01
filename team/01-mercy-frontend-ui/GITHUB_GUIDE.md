# GitHub Guide

```powershell
git switch develop
git pull origin develop
git switch -c frontend/mercy
cd frontend
npm install
npm run lint
npm test -- --run
npm run build
git status
git add <owned-files>
git commit -m "feat(frontend): describe completed work"
git push -u origin frontend/mercy
```

Open a pull request into `develop`. Include summary, changed files, commands/results,
screenshots when visual, known limits, and the linked issue. Never commit `.env`.
