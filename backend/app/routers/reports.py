from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.models.user import User
from app.db.session import get_db
from app.schemas.report import (
    AuditLogResponse,
    RawSQLRequest,
    SQLQueryExecutionResult,
    SQLQueryMetadata,
)
from app.services.auth_service import get_current_admin, get_current_user
from app.services.report_service import ReportService, get_report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/queries",
    response_model=List[SQLQueryMetadata],
    summary="List all 18 pre-built DBMS benchmark queries",
)
def list_queries(
    report_service: ReportService = Depends(get_report_service),
) -> List[SQLQueryMetadata]:
    """Returns metadata for all 18 DBMS analytical queries demonstrating joins, views, subqueries, and window functions."""
    return report_service.list_available_queries()


@router.get(
    "/queries/{query_id}",
    response_model=SQLQueryExecutionResult,
    summary="Execute a pre-built DBMS query by ID (Q01-Q18)",
)
def execute_query(
    query_id: str,
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service),
) -> SQLQueryExecutionResult:
    """Executes one of the 18 pre-built analytical queries against the database and returns structured tabular results."""
    return report_service.execute_predefined_query(db=db, query_id=query_id)


@router.post(
    "/execute-sql",
    response_model=SQLQueryExecutionResult,
    summary="Interactive SQL Playground runner",
)
def execute_custom_sql(
    request: RawSQLRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service),
) -> SQLQueryExecutionResult:
    """Executes an authorized read-only SQL query against the database engine for live evaluation."""
    return report_service.execute_custom_sql(db=db, raw_sql=request.sql)


@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    summary="Retrieve trigger-generated mutation logs from trip_audit",
)
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    report_service: ReportService = Depends(get_report_service),
) -> List[AuditLogResponse]:
    """Retrieves row-level JSONB before/after snapshots captured by the PL/pgSQL trg_trip_audit trigger."""
    return report_service.get_audit_logs(db=db, limit=limit)
