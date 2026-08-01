# Risk Register

| Risk | Prob. | Impact | Prevention | Backup action | Owner |
|---|---|---|---|---|---|
| Merge conflicts | M | H | small PRs/file ownership | one merge owner, pair resolve | Yasmin |
| Late schema change | M | H | M1 freeze/migrations | impact review + versioned migration | Samyuktha |
| API mismatch | H | H | contract examples/tests | adapter or coordinated v2 | Yasmin/Mercy |
| Missing API key | H | M | mock default | deterministic mock demo | Madhu |
| AI unstable/invalid | M | H | schema validation/timeout | mock fallback | Madhu |
| PostgreSQL setup | M | H | versioned runbook | prepared demo DB/restore | Penitta |
| Frontend/backend connection | M | H | env URL/CORS smoke | documented local ports | Mercy/Yasmin |
| Incomplete seed data | M | M | seed checklist | minimal golden fixture | Sashtika |
| Member delay | M | H | weekly board/blockers | re-scope/support assignment | Yasmin |
| Insufficient tests | M | H | DoD/CI checklist | freeze features, test core flow | Eunice |
| Presentation failure | L | H | two rehearsals | screenshots/video/local backup | Eunice |
| Secret leakage | L | H | ignore/scanning/review | revoke/rotate/remove history | Yasmin |
| Last-minute features | H | H | M5 freeze | defer to future work | Yasmin |

<!-- SUPABASE_UPDATE_START -->
## Supabase risks

| Risk | Probability | Impact | Prevention | Responsible | Backup plan |
|---|---|---|---|---|---|
| Supabase internet dependency | M | H | mock/offline plan and early checks | Penitta | optional migration-built local DB + screenshots |
| Incorrect connection string | M | H | Dashboard copy, URL encode, health check | Yasmin | rotate/reissue and use documented mode |
| Pooling incompatibility | M | H | test direct/session/transaction needs | Penitta | use direct/session-compatible migration URI |
| Service-role exposure | L | Critical | keep backend-only/unused, secret scan | Yasmin | revoke immediately and inspect history |
| Dashboard change missing from Git | M | H | no manual completion; PR gate | Samyuktha | reproduce migration/SQL then reset drift |
| Alembic/SQL DDL conflict | M | H | explicit object ownership | Yasmin/Sashtika | rebuild safe dev DB from reviewed source |
| Free-tier limit/pause | M | M | confirm current plan and activity | Penitta | export backup/local demo fallback |
| Migration mismatch | M | H | current/history in PR and status | Yasmin | reconcile revisions before integration |
| Public table exposure | L | Critical | exposure/permissions review | Penitta | disable access, rotate keys, investigate |
| Missing RLS after direct access | L | Critical | architecture review and policy tests | Yasmin | remove direct access until policies pass |
| Network demo failure | M | H | rehearsal and offline pack | Eunice | screenshots/API samples/recording/local fallback |
<!-- SUPABASE_UPDATE_END -->
