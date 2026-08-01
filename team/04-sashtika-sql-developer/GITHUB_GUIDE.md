# GitHub Guide

```powershell
git switch develop
git pull origin develop
git switch -c sql/sashtika
psql -U roamgenie_app -d roamgenie -f database/schema/001_schema.sql
psql -U roamgenie_app -d roamgenie -f database/tests/001_constraints.sql
git status
git add <owned-files>
git commit -m "feat(database): describe completed work"
git push -u origin sql/sashtika
```

Open a pull request into `develop`. Include summary, changed files, commands/results,
screenshots when visual, known limits, and the linked issue. Never commit `.env`.
