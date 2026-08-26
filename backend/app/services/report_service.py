import re
import time
from typing import Any, Dict, List, Optional, Set
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.report import (
    AuditLogResponse,
    SQLQueryExecutionResult,
    SQLQueryMetadata,
)

# Allowed starting tokens for read-only analytical queries
ALLOWED_STARTING_TOKENS: Set[str] = {"select", "with", "explain"}

# Disallowed mutating SQL keywords / administrative commands
DISALLOWED_MUTATING_KEYWORDS: Set[str] = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "truncate",
    "create",
    "grant",
    "revoke",
    "call",
    "copy",
    "vacuum",
    "execute",
    "lock",
    "merge",
    "reindex",
    "cluster",
    "into",
    "transaction",
    "commit",
    "rollback",
    "savepoint",
    "set",
    "show",
}

# Blocked sensitive tables and columns that must never be accessed via the custom query runner
BLOCKED_SENSITIVE_ENTITIES: Set[str] = {
    "users",
    "user_preferences",
    "password_hash",
    "password",
}

# Output columns that must always be redacted if present in result sets (defense-in-depth)
SENSITIVE_OUTPUT_COLUMNS: Set[str] = {
    "password_hash",
    "password",
}

REPORT_QUERIES: Dict[str, SQLQueryMetadata] = {
    "Q01": SQLQueryMetadata(
        id="Q01",
        title="Active Destinations Ordered by Daily Cost",
        category="Simple Filter & Sorting",
        description="Selects active travel destinations sorted in ascending order of average daily cost.",
        sql="SELECT city, country, average_daily_cost FROM destinations WHERE active = true ORDER BY average_daily_cost ASC;",
    ),
    "Q02": SQLQueryMetadata(
        id="Q02",
        title="Hotels with Destination Details (INNER JOIN)",
        category="Relational Joins",
        description="Performs an INNER JOIN between destinations and hotels to list accommodations and nightly tariffs.",
        sql="SELECT d.city, h.name AS hotel_name, h.price_per_night, h.rating FROM destinations d JOIN hotels h ON h.destination_id = d.id ORDER BY h.price_per_night ASC;",
    ),
    "Q03": SQLQueryMetadata(
        id="Q03",
        title="Destination Attraction Density (LEFT JOIN & GROUP BY)",
        category="Aggregations & Outer Joins",
        description="Uses a LEFT OUTER JOIN to aggregate total sightseeing attractions per destination city.",
        sql="SELECT d.city, COUNT(a.id) AS attraction_count FROM destinations d LEFT JOIN attractions a ON a.destination_id = d.id GROUP BY d.id, d.city ORDER BY attraction_count DESC;",
    ),
    "Q04": SQLQueryMetadata(
        id="Q04",
        title="Dining Catalogue Coverage (Outer Join)",
        category="Relational Joins",
        description="Evaluates culinary options across destinations preserving catalogue completeness.",
        sql="SELECT d.city, r.name AS restaurant_name, r.cuisine, r.average_cost_per_person, r.rating FROM destinations d LEFT JOIN restaurants r ON r.destination_id = d.id ORDER BY d.city, r.name;",
    ),
    "Q05": SQLQueryMetadata(
        id="Q05",
        title="Multi-Table Trip Summary (Trips + Users + Destinations)",
        category="Multi-Table Joins",
        description="Joins 3 core normalized tables to display user trip bookings, destination city, and allocated budgets.",
        sql="SELECT t.id AS trip_id, u.email, d.city, t.total_budget, t.status FROM trips t JOIN users u ON u.id = t.user_id JOIN destinations d ON d.id = t.destination_id ORDER BY t.created_at DESC;",
    ),
    "Q06": SQLQueryMetadata(
        id="Q06",
        title="Aggregate Expenses by Trip and Category",
        category="Grouping & Aggregation",
        description="Sums recorded expenses grouped by trip and spending category (Food, Transport, Lodging, etc.).",
        sql="SELECT trip_id, category, SUM(amount) AS total_spent FROM expenses GROUP BY trip_id, category ORDER BY trip_id, total_spent DESC;",
    ),
    "Q07": SQLQueryMetadata(
        id="Q07",
        title="Trips with Budget Deficits (Computed Arithmetic)",
        category="Conditional Filters & Math",
        description="Identifies trips where total estimated costs exceed allocated user budget and computes the exact deficit.",
        sql="SELECT id AS trip_id, total_budget, estimated_total, (estimated_total - total_budget) AS deficit FROM trips WHERE estimated_total > total_budget ORDER BY deficit DESC;",
    ),
    "Q08": SQLQueryMetadata(
        id="Q08",
        title="Above-Average Priced Accommodations (Scalar Subquery)",
        category="Subqueries",
        description="Finds premium hotels whose nightly price exceeds the global average hotel tariff.",
        sql="SELECT name, price_per_night, rating FROM hotels WHERE price_per_night > (SELECT AVG(price_per_night) FROM hotels) ORDER BY price_per_night DESC;",
    ),
    "Q09": SQLQueryMetadata(
        id="Q09",
        title="Top-Rated Attraction per City (Correlated Subquery)",
        category="Correlated Subqueries",
        description="Finds the highest-rated point of interest in each destination using a correlated subquery.",
        sql="SELECT d.city, a.name AS top_attraction, a.rating FROM destinations d JOIN attractions a ON a.destination_id = d.id WHERE a.rating = (SELECT MAX(x.rating) FROM attractions x WHERE x.destination_id = d.id) ORDER BY d.city;",
    ),
    "Q10": SQLQueryMetadata(
        id="Q10",
        title="Complete Day-Wise Itinerary Schedule (3-Tier Join)",
        category="Multi-Table Joins",
        description="Traverses itineraries -> itinerary_days -> itinerary_items to render sequential daily itineraries.",
        sql="SELECT i.trip_id, dy.day_number, it.item_order, it.title, it.category, it.estimated_cost FROM itineraries i JOIN itinerary_days dy ON dy.itinerary_id = i.id JOIN itinerary_items it ON it.itinerary_day_id = dy.id ORDER BY i.trip_id, dy.day_number, it.item_order;",
    ),
    "Q11": SQLQueryMetadata(
        id="Q11",
        title="Saved Trip Bookmarks per User",
        category="Aggregation & Outer Joins",
        description="Counts the number of trips bookmarked by each registered user.",
        sql="SELECT u.email, COUNT(s.id) AS saved_count FROM users u LEFT JOIN saved_trips s ON s.user_id = u.id GROUP BY u.id, u.email ORDER BY saved_count DESC;",
    ),
    "Q12": SQLQueryMetadata(
        id="Q12",
        title="Average Destination Review Ratings",
        category="Aggregations & Rounding",
        description="Computes mean user review score and feedback volume per destination.",
        sql="SELECT d.city, ROUND(AVG(rv.rating), 2) AS user_rating FROM destinations d LEFT JOIN reviews rv ON rv.destination_id = d.id GROUP BY d.id, d.city ORDER BY user_rating DESC;",
    ),
    "Q13": SQLQueryMetadata(
        id="Q13",
        title="Budget Allocation Distribution (Window Function)",
        category="Window Functions",
        description="Computes category spending allocation percentages for each trip using PARTITION BY.",
        sql="SELECT trip_id, category, amount, ROUND(amount * 100.0 / NULLIF(SUM(amount) OVER (PARTITION BY trip_id), 0), 2) AS pct FROM budget_allocations ORDER BY trip_id, amount DESC;",
    ),
    "Q14": SQLQueryMetadata(
        id="Q14",
        title="Packing Progress Metrics (Conditional Aggregates)",
        category="Aggregations & CASE",
        description="Calculates packed items versus total checklist items for each trip.",
        sql="SELECT trip_id, SUM(CASE WHEN is_packed = true THEN 1 ELSE 0 END) AS packed, COUNT(*) AS total FROM packing_items GROUP BY trip_id ORDER BY trip_id;",
    ),
    "Q15": SQLQueryMetadata(
        id="Q15",
        title="AI Conversation Interaction Volume",
        category="Aggregation & Joins",
        description="Tracks engagement by measuring the number of AI assistant messages logged per conversation.",
        sql="SELECT c.id AS conversation_id, c.user_id, COUNT(m.id) AS messages FROM ai_conversations c LEFT JOIN ai_messages m ON m.conversation_id = c.id GROUP BY c.id, c.user_id ORDER BY messages DESC;",
    ),
    "Q16": SQLQueryMetadata(
        id="Q16",
        title="Budget-Friendly Transport Routes",
        category="Filtered Joins",
        description="Filters transit connections (flights, trains, buses) under an economical threshold.",
        sql="SELECT d.city, t.mode, t.provider, t.estimated_cost FROM transport_options t JOIN destinations d ON d.id = t.destination_id WHERE t.estimated_cost <= 2500 ORDER BY t.estimated_cost ASC;",
    ),
    "Q17": SQLQueryMetadata(
        id="Q17",
        title="Recent Destination Weather Observations",
        category="Time-Series & Sorting",
        description="Retrieves the latest cached weather snapshots for destination climate monitoring.",
        sql="SELECT d.city, w.observed_at, w.summary, w.temperature_c FROM weather_snapshots w JOIN destinations d ON d.id = w.destination_id ORDER BY w.observed_at DESC;",
    ),
    "Q18": SQLQueryMetadata(
        id="Q18",
        title="Heritage-Focused Travellers (EXISTS Subquery)",
        category="Correlated Subqueries & EXISTS",
        description="Identifies users who configured 'heritage' in their activity preferences using an EXISTS clause.",
        sql="SELECT u.full_name, u.email FROM users u WHERE EXISTS (SELECT 1 FROM activity_preferences p WHERE p.user_id = u.id AND (p.activity = 'heritage' OR p.activity = 'palaces')) ORDER BY u.id;",
    ),
}


class ReportService:
    """Service for executing DBMS analytical benchmark queries, inspecting database views, and auditing."""

    def list_available_queries(self) -> List[SQLQueryMetadata]:
        return list(REPORT_QUERIES.values())

    def execute_predefined_query(self, db: Session, query_id: str) -> SQLQueryExecutionResult:
        query_meta = REPORT_QUERIES.get(query_id.upper())
        if not query_meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Query '{query_id}' not found. Available queries: {list(REPORT_QUERIES.keys())}",
            )
        return self._execute_raw_sql(db=db, sql=query_meta.sql, query_id=query_meta.id, title=query_meta.title, category=query_meta.category)

    def _sanitize_and_validate_custom_sql(self, raw_sql: str) -> str:
        """
        Validates user-supplied custom SQL against statement rules, mutating keywords,
        multiple statement injections, and sensitive entity references.
        Returns the cleaned, single-statement SQL string.
        """
        if not raw_sql or not raw_sql.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SQL query cannot be empty.",
            )

        # 1. Strip multi-line comments (/* ... */) and single-line comments (-- ...)
        cleaned = re.sub(r"/\*[\s\S]*?\*/", " ", raw_sql)
        cleaned = re.sub(r"--[^\r\n]*", " ", cleaned)
        cleaned = cleaned.strip()

        if not cleaned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SQL query contains only comments or whitespace.",
            )

        # 2. Semicolon and multi-statement injection check
        # Allow a single trailing semicolon, but reject multiple non-empty statements
        statements = [s.strip() for s in cleaned.split(";") if s.strip()]
        if len(statements) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multiple SQL statements are not permitted in a single query execution.",
            )
        single_sql = statements[0]

        # 3. Strip string literals ('...' and $$...$$) for token inspection
        # This prevents matching false-positive literals (e.g. WHERE city = 'users')
        no_literals = re.sub(r"'(''|[^'])*'", " '' ", single_sql)
        no_literals = re.sub(r"\$\$[\s\S]*?\$\$", " '' ", no_literals)
        # Remove identifier quotes (double quotes, backticks, brackets) so "Users" becomes Users
        no_literals = re.sub(r'["`\[\]]', " ", no_literals)

        # 4. Extract word tokens
        tokens = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", no_literals.lower())
        if not tokens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid SQL tokens found.",
            )

        # 5. First token must be a read-only query statement
        first_token = tokens[0]
        if first_token not in ALLOWED_STARTING_TOKENS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interactive query runner is restricted to read-only statements (SELECT, WITH, EXPLAIN).",
            )

        # 6. Check for disallowed mutating keywords anywhere in the query
        for token in tokens:
            if token in DISALLOWED_MUTATING_KEYWORDS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Disallowed mutating SQL keyword '{token}' detected.",
                )

        # 7. Check for sensitive tables and columns
        for token in tokens:
            if token in BLOCKED_SENSITIVE_ENTITIES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Access to sensitive identity and credential tables is restricted for security.",
                )

        return single_sql

    def execute_custom_sql(self, db: Session, raw_sql: str) -> SQLQueryExecutionResult:
        """Executes an authorized read-only SQL query safely in the SQL query playground."""
        validated_sql = self._sanitize_and_validate_custom_sql(raw_sql)
        return self._execute_raw_sql(
            db=db,
            sql=validated_sql,
            query_id="CUSTOM",
            title="Custom SQL Execution",
            category="Interactive SQL Playground",
        )

    def get_audit_logs(self, db: Session, limit: int = 50) -> List[AuditLogResponse]:
        """Fetches latest row-level mutation logs captured by the PL/pgSQL trip_audit trigger."""
        try:
            stmt = text("SELECT id, trip_id, action, changed_at, changed_by, old_row, new_row FROM trip_audit ORDER BY changed_at DESC LIMIT :limit")
            result = db.execute(stmt, {"limit": limit})
            logs = []
            for row in result.mappings():
                logs.append(
                    AuditLogResponse(
                        id=row["id"],
                        trip_id=row.get("trip_id"),
                        action=row["action"],
                        changed_at=row["changed_at"],
                        changed_by=row.get("changed_by"),
                        old_row=row.get("old_row"),
                        new_row=row.get("new_row"),
                    )
                )
            return logs
        except Exception:
            return []

    def _execute_raw_sql(
        self,
        db: Session,
        sql: str,
        query_id: str,
        title: str,
        category: str,
    ) -> SQLQueryExecutionResult:
        start_time = time.perf_counter()
        try:
            result = db.execute(text(sql))
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0

            columns = list(result.keys()) if result.returns_rows else []
            raw_rows = result.mappings().all() if result.returns_rows else []

            formatted_rows: List[Dict[str, Any]] = []
            for r in raw_rows:
                row_dict: Dict[str, Any] = {}
                for col in columns:
                    val = r[col]
                    if col.lower() in SENSITIVE_OUTPUT_COLUMNS:
                        row_dict[col] = "[REDACTED]"
                    elif hasattr(val, "isoformat"):
                        row_dict[col] = val.isoformat()
                    else:
                        row_dict[col] = val
                formatted_rows.append(row_dict)

            return SQLQueryExecutionResult(
                query_id=query_id,
                title=title,
                category=category,
                sql=sql,
                columns=columns,
                rows=formatted_rows,
                row_count=len(formatted_rows),
                execution_time_ms=round(execution_time_ms, 2),
            )
        except Exception as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SQL Execution Error: {str(exc)}",
            )


_report_service = ReportService()


def get_report_service() -> ReportService:
    return _report_service
