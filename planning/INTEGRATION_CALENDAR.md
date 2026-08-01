# Integration Calendar

| Checkpoint | Participants | Contract/evidence | Gate |
|---|---|---|---|
| M0 day 2 | all | clone/setup on two systems | planning to develop |
| M1 midweek | Mercy/Yasmin/Samyuktha/Madhu | fields, errors, tables, AI JSON | v1 freeze |
| M2 midweek | Mercy/Yasmin/Penitta/Eunice | register/login + real PostgreSQL | auth smoke |
| M3 week 3 | catalogue owners | destination DB→UI slice | pattern approved |
| M3 week 4 | catalogue owners | remaining modules in small batches | integration tests |
| M4 twice weekly | all relevant | trip save; AI validation; itinerary save/reopen | full journey |
| M5 start/end | all | feature freeze then RC tests/restore | rc1 |
| M6 mid/end | all | two rehearsals then clean clone | v1.0.0 |

Yasmin schedules meetings; owners bring contract diff, test output and blocker. Never defer all integration to milestone end.

<!-- SUPABASE_UPDATE_START -->
## Supabase checkpoints

M0: empty Supabase DB health. M1: ERD/ORM/migration/SQL ownership review. M2: auth persisted and visible in Table Editor. M3: catalogue DB→API→React plus SQL/index evidence. M4: transactional itinerary save/reopen plus Dashboard verification. M5: outage/security/fresh recreation/restore. M6: online and offline database demo rehearsal.
<!-- SUPABASE_UPDATE_END -->
