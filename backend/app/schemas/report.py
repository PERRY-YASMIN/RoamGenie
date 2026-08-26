from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SQLQueryMetadata(BaseModel):
    id: str = Field(..., description="Query identifier (e.g., Q01, Q02)")
    title: str = Field(..., description="Human-readable title")
    category: str = Field(..., description="DBMS concept category (e.g., JOIN, Subquery, Window Function)")
    description: str = Field(..., description="Detailed description of the relational concept demonstrated")
    sql: str = Field(..., description="The SQL query text")


class SQLQueryExecutionResult(BaseModel):
    query_id: str
    title: str
    category: str
    sql: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time_ms: float


class RawSQLRequest(BaseModel):
    sql: str = Field(..., min_length=5, max_length=5000, description="Raw SELECT query to execute in the DBMS query runner")


class AuditLogResponse(BaseModel):
    id: int
    trip_id: Optional[int] = None
    action: str
    changed_at: datetime
    changed_by: Optional[str] = None
    old_row: Optional[Dict[str, Any]] = None
    new_row: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ViewBudgetSummaryResponse(BaseModel):
    trip_id: int
    city: Optional[str] = None
    total_budget: Decimal
    estimated_total: Decimal
    remaining_budget: Decimal
    is_over_budget: bool

    model_config = ConfigDict(from_attributes=True)


class ViewDestinationCatalogueResponse(BaseModel):
    id: int
    city: str
    country: str
    base_daily_cost: Decimal
    hotel_count: int
    restaurant_count: int
    attraction_count: int

    model_config = ConfigDict(from_attributes=True)
