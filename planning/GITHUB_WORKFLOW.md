# GitHub Workflow

Long-lived: `main` stable, `develop` integrated. Member branches: `frontend/mercy`, `backend/yasmin`, `database-design/samyuktha`, `sql/sashtika`, `ai/madhu`, `dba/penitta`, `backend-presentation/eunice`. Short-lived examples: `frontend/login-ui`, `backend/auth-api`, `sql/create-trip-tables`, `ai/itinerary-service`.

```powershell
git clone <repository-url> RoamGenie
cd RoamGenie
git switch develop
git pull origin develop
git switch -c frontend/login-ui
git status
git add frontend tests/frontend
git commit -m "feat(frontend): add trip input form"
git push -u origin frontend/login-ui
gh pr create --base develop --fill
git fetch origin
git rebase origin/develop
# resolve each marked file, then:
git add <resolved-file>
git rebase --continue
git log --oneline --graph --decorate -15
```

Never push unfinished work to `main`. Use small commits and test before push. PR: completed work, files, test commands/results, screenshots, limits and issue. Relevant teammate reviews; Yasmin performs integration review; resolve conflicts on the feature branch. After acceptance merge `develop` to `main` and tag: `git tag -a milestone-1 -m "Milestone 1 accepted"; git push origin milestone-1`.

Commit examples: `feat(auth): implement JWT login`, `feat(database): add itinerary tables`, `feat(ai): add itinerary prompt service`, `test(api): add trip endpoint tests`, `fix(sql): correct expense trigger`, `docs(plan): update milestone checklist`.

## Main-branch ownership

`PERRY-YASMIN` is the sole code owner in `.github/CODEOWNERS`. Protect `main` in GitHub by requiring a pull request, one approval, Code Owner review, conversation resolution, no force pushes and no deletion. Teammates target `develop`; Yasmin alone performs the accepted `develop` → `main` release.

Because this repository is owned by a personal GitHub account, collaborators receive repository write access and personal repositories do not provide the organization-only “Restrict who can push” actor list. For absolute enforcement, transfer the repository to a GitHub organization and restrict `main` pushes/bypass to Yasmin, or do not add collaborators and have teammates contribute through forks. CODEOWNERS plus required review is the strongest review gate while retaining collaborators on this personal repository, but it is not identical to an organization-level owner-only push restriction.

<!-- SUPABASE_UPDATE_START -->
## Database change workflow

Schema PR sequence: design issue → Samyuktha approval → SQLAlchemy model → reviewed Alembic migration → related SQL → safe development test → upgrade/downgrade where practical → dictionary/API/frontend updates → PR with exact migration steps → apply after review → status update. Dashboard-only changes are forbidden.

Commit examples: `feat(database): configure Supabase PostgreSQL connection`; `feat(migrations): add initial travel schema`; `feat(sql): add itinerary reporting views`; `fix(database): correct trip foreign key`; `docs(supabase): add hosted PostgreSQL setup guide`; `test(database): verify Supabase constraints`; `chore(env): add safe database placeholders`.
<!-- SUPABASE_UPDATE_END -->
