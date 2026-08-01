# Dependency Matrix

| Consumer | Needs | Provider | Wait condition |
|---|---|---|---|
| Mercy | request/response/errors | Yasmin | API v1 freeze |
| Yasmin | keys/relations/constraints | Samyuktha | schema v1 approval |
| Sashtika | relational schema | Samyuktha | design review signed |
| Madhu | trip DTO and allow-listed records | Yasmin/Samyuktha | AI contract freeze |
| Penitta | reviewed SQL/migrations | Sashtika/Yasmin | clean replay passes |
| Eunice | stable endpoints/build | module owners | PR merged to develop |
| Everyone | current integration base | Yasmin/PR owners | timely `develop` merge |

While waiting, work only on mocks, tests, docs or fixtures matching the draft contract; do not silently freeze a dependency yourself.

<!-- SUPABASE_UPDATE_START -->
## Supabase dependencies

Yasmin and Penitta need the selected Dashboard connection mode and secret delivery. Migrations wait for Samyuktha design approval and Sashtika DDL-ownership review. Mercy waits for FastAPI contracts, never database access. Madhu waits for backend-provided structured records. Eunice waits for migrated/seeded Supabase data and stable APIs.
<!-- SUPABASE_UPDATE_END -->
