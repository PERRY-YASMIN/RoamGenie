import pytest
from fastapi.testclient import TestClient


# ============================================================================
# 18 PREDEFINED ANALYTICAL DBMS QUERIES
# ============================================================================


def test_list_all_18_queries(client: TestClient):
    """Verify metadata listing for all 18 DBMS analytical queries."""
    response = client.get("/api/v1/reports/queries")
    assert response.status_code == 200
    queries = response.json()
    assert len(queries) == 18
    query_ids = [q["id"] for q in queries]
    for i in range(1, 19):
        assert f"Q{i:02d}" in query_ids


def test_execute_predefined_query_q01(client: TestClient, seed_destination):
    """Verify execution of Q01 (Simple Filter & Sorting)."""
    response = client.get("/api/v1/reports/queries/Q01")
    assert response.status_code == 200
    data = response.json()
    assert data["query_id"] == "Q01"
    assert "city" in data["columns"]
    assert data["row_count"] >= 1
    assert data["execution_time_ms"] >= 0


def test_execute_predefined_query_q02_join(client: TestClient, seed_destination):
    """Verify execution of Q02 (Relational Joins)."""
    response = client.get("/api/v1/reports/queries/Q02")
    assert response.status_code == 200
    data = response.json()
    assert data["query_id"] == "Q02"
    assert "hotel_name" in data["columns"]


def test_execute_all_18_predefined_queries(client: TestClient, seed_destination):
    """Verify that every single predefined analytical query (Q01-Q18) executes without SQL errors."""
    for i in range(1, 19):
        qid = f"Q{i:02d}"
        response = client.get(f"/api/v1/reports/queries/{qid}")
        assert response.status_code == 200, f"Query {qid} failed with {response.status_code}: {response.text}"
        data = response.json()
        assert data["query_id"] == qid
        assert isinstance(data["columns"], list)
        assert isinstance(data["rows"], list)


def test_execute_predefined_query_invalid_id(client: TestClient):
    """Verify that querying a non-existent query ID returns 404."""
    response = client.get("/api/v1/reports/queries/Q99")
    assert response.status_code == 404


# ============================================================================
# CUSTOM SQL PLAYGROUND SECURITY & RBAC
# ============================================================================


def test_custom_sql_anonymous_rejected(client: TestClient):
    """Security Gate: Anonymous callers without Authorization header must be rejected with 401."""
    response = client.post(
        "/api/v1/reports/execute-sql",
        json={"sql": "SELECT id, city, country FROM destinations;"},
    )
    assert response.status_code == 401
    assert "Authentication token required" in str(response.json())


def test_custom_sql_invalid_token_rejected(client: TestClient):
    """Security Gate: Callers with invalid or forged JWT tokens must be rejected with 401."""
    response = client.post(
        "/api/v1/reports/execute-sql",
        headers={"Authorization": "Bearer invalid.token.value"},
        json={"sql": "SELECT id, city, country FROM destinations;"},
    )
    assert response.status_code == 401


def test_custom_sql_traveller_role_rejected(client: TestClient, traveller_headers: dict):
    """Security Gate: Non-admin users with 'traveller' role must be rejected with 403 Forbidden."""
    response = client.post(
        "/api/v1/reports/execute-sql",
        headers=traveller_headers,
        json={"sql": "SELECT id, city, country FROM destinations;"},
    )
    assert response.status_code == 403
    assert "Administrator access required" in str(response.json())


def test_custom_sql_admin_allowed_readonly(
    client: TestClient, admin_headers: dict, seed_destination
):
    """Security Gate: Authenticated admin users can execute legitimate analytical SELECT queries."""
    response = client.post(
        "/api/v1/reports/execute-sql",
        headers=admin_headers,
        json={"sql": "SELECT id, city, country, average_daily_cost FROM destinations WHERE active = true OR active = 1;"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_id"] == "CUSTOM"
    assert "city" in data["columns"]
    assert data["row_count"] >= 1


def test_custom_sql_admin_with_clause_and_explain(
    client: TestClient, admin_headers: dict, seed_destination
):
    """Verify that authorized read-only statements starting with WITH (CTE) or EXPLAIN are allowed."""
    # WITH clause (CTE)
    cte_resp = client.post(
        "/api/v1/reports/execute-sql",
        headers=admin_headers,
        json={"sql": "WITH active_dests AS (SELECT id, city FROM destinations WHERE active = true OR active = 1) SELECT city FROM active_dests;"},
    )
    assert cte_resp.status_code == 200
    assert "city" in cte_resp.json()["columns"]

    # EXPLAIN statement
    explain_resp = client.post(
        "/api/v1/reports/execute-sql",
        headers=admin_headers,
        json={"sql": "EXPLAIN SELECT id, city FROM destinations;"},
    )
    assert explain_resp.status_code == 200


def test_custom_sql_rejects_empty_and_whitespace(
    client: TestClient, admin_headers: dict
):
    """Verify rejection of empty, whitespace-only, or comment-only SQL inputs."""
    # Empty
    r1 = client.post("/api/v1/reports/execute-sql", headers=admin_headers, json={"sql": ""})
    assert r1.status_code in (400, 422)

    # Whitespace
    r2 = client.post("/api/v1/reports/execute-sql", headers=admin_headers, json={"sql": "       "})
    assert r2.status_code in (400, 422)

    # Comment only
    r3 = client.post("/api/v1/reports/execute-sql", headers=admin_headers, json={"sql": "-- just a comment\n/* another comment */"})
    assert r3.status_code in (400, 422)


# ============================================================================
# MUTATING KEYWORD & DDL/DML REJECTION
# ============================================================================


@pytest.mark.parametrize(
    "mutating_sql",
    [
        "DELETE FROM destinations;",
        "INSERT INTO destinations (city, country) VALUES ('Test', 'Country');",
        "UPDATE destinations SET active = false;",
        "DROP TABLE hotels;",
        "ALTER TABLE destinations ADD COLUMN test_col VARCHAR(50);",
        "TRUNCATE TABLE attractions;",
        "CREATE TABLE test_table (id INT);",
        "GRANT ALL PRIVILEGES ON destinations TO public;",
        "REVOKE SELECT ON destinations FROM public;",
        "dElEtE FROM destinations;",
        "/* comment */ DROP TABLE destinations;",
        "-- comment\nDELETE FROM destinations;",
    ],
)
def test_custom_sql_rejects_mutating_keywords(
    client: TestClient, admin_headers: dict, mutating_sql: str
):
    """Verify that all DDL, DML, and mutating statements are strictly rejected with 400."""
    response = client.post(
        "/api/v1/reports/execute-sql",
        headers=admin_headers,
        json={"sql": mutating_sql},
    )
    assert response.status_code == 400
    detail = str(response.json()).lower()
    assert "read-only" in detail or "disallowed" in detail or "restricted" in detail


def test_custom_sql_rejects_multi_statement_injection(
    client: TestClient, admin_headers: dict
):
    """Verify that semicolon-chained multiple statements are strictly rejected."""
    chained_sqls = [
        "SELECT id FROM destinations; DROP TABLE hotels;",
        "SELECT id FROM destinations; DELETE FROM destinations;",
        "SELECT 1; SELECT 2;",
    ]
    for sql in chained_sqls:
        response = client.post(
            "/api/v1/reports/execute-sql",
            headers=admin_headers,
            json={"sql": sql},
        )
        assert response.status_code == 400
        assert "multiple" in str(response.json()).lower()


# ============================================================================
# SENSITIVE TABLE & CREDENTIAL PROTECTION
# ============================================================================


@pytest.mark.parametrize(
    "sensitive_sql",
    [
        # Direct SELECT on users
        "SELECT * FROM users;",
        "SELECT id, email, password_hash FROM users;",
        "SELECT email FROM Users;",
        'SELECT * FROM "users";',
        'SELECT * FROM "Users";',
        "SELECT * FROM public.users;",
        'SELECT * FROM public."users";',
        # Direct SELECT on user_preferences
        "SELECT * FROM user_preferences;",
        'SELECT * FROM "user_preferences";',
        "SELECT * FROM public.user_preferences;",
        # Subqueries and joins referencing users
        "SELECT d.city FROM destinations d WHERE d.id IN (SELECT user_id FROM user_preferences);",
        "SELECT d.city FROM destinations d JOIN users u ON u.id = d.id;",
        "SELECT (SELECT password_hash FROM users LIMIT 1);",
        "SELECT * FROM (SELECT * FROM users) AS u;",
        # Comments attempting obfuscation
        "SELECT * FROM /* comments */ users;",
        "SELECT * FROM -- comment\nusers;",
        # Column extraction
        "SELECT password_hash FROM destinations;",
    ],
)
def test_custom_sql_rejects_sensitive_tables_and_credentials(
    client: TestClient, admin_headers: dict, sensitive_sql: str
):
    """Verify that any query attempting to inspect users, user_preferences, or credentials is blocked."""
    response = client.post(
        "/api/v1/reports/execute-sql",
        headers=admin_headers,
        json={"sql": sensitive_sql},
    )
    assert response.status_code == 400
    assert "sensitive" in str(response.json()).lower() or "restricted" in str(response.json()).lower()


def test_custom_sql_allows_string_literal_containing_entity_name(
    client: TestClient, admin_headers: dict, seed_destination
):
    """Verify that legitimate string literals in WHERE clauses (e.g. city = 'users') are not falsely blocked."""
    response = client.post(
        "/api/v1/reports/execute-sql",
        headers=admin_headers,
        json={"sql": "SELECT id, city, country FROM destinations WHERE city = 'users';"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query_id"] == "CUSTOM"
    assert "city" in data["columns"]


# ============================================================================
# AUDIT LOGS ENDPOINT
# ============================================================================


def test_get_audit_logs_endpoint(client: TestClient):
    """Verify that the trip audit logs endpoint returns a list."""
    response = client.get("/api/v1/reports/audit-logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
