# Workspace Implementation Plan

## Audit assumptions

The target repository was empty, so use the brief's default React/Vite + FastAPI + PostgreSQL + provider-neutral AI stack. Preserve all parent `../docs` course assets unchanged and do not import their older SQL until schema comparison/provenance review.

## Create/modify

Create root governance guides; focused `docs`, `planning`, `presentation`; 16 distinct handbook files for each of seven members; frontend/backend/database/AI/test/script starters. No pre-existing target file requires modification.

## Risks

Templates could be mistaken for finished modules, old course SQL may conflict, contracts may drift, and local Python/PostgreSQL versions may differ. Mitigate with explicit TODO/status labels, M1 freezes, migrations, mock AI, clean-clone checks and owner reviews.

## Expected structure

Root source-of-truth documents → team handbooks → layer folders (`frontend`, `backend`, `database`, `ai`) → cross-layer `tests`/`scripts` → presentation evidence. Keep one source of truth and link rather than duplicating long explanations.

