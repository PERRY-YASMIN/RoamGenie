# Testing Strategy

Use a pyramid: pure unit tests for budget/AI validation; repository/database tests for constraints and SQL objects; API tests for auth/CRUD/errors; a small set of UI tests; full integration and manual acceptance journey. Every bug gets a failing regression test where practical. Test doubles are allowed for AI/weather, not for claiming PostgreSQL integration. Commands and ownership: `../TESTING_GUIDE.md`.
