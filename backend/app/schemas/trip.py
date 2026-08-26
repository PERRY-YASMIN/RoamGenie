from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ============================================================================
# TRIP MEMBERS
# ============================================================================


class TripMemberCreateRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    age_group: Optional[str] = Field(default=None, max_length=30)
    special_requirements: Optional[str] = Field(default=None, max_length=500)


class TripMemberResponse(BaseModel):
    id: int
    trip_id: int
    display_name: str
    age_group: Optional[str] = None
    special_requirements: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# PACKING ITEMS
# ============================================================================


class PackingItemCreateRequest(BaseModel):
    item: str = Field(min_length=1, max_length=120)
    category: Optional[str] = Field(default=None, max_length=40)
    is_packed: bool = False


class PackingItemResponse(BaseModel):
    id: int
    trip_id: int
    item: str
    category: Optional[str] = None
    is_packed: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ITINERARY & ITEMS
# ============================================================================


class ItineraryItemResponse(BaseModel):
    id: int
    itinerary_day_id: int
    item_order: int
    start_time: Optional[time] = None
    title: str
    category: str
    estimated_cost: Decimal
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ItineraryItemSwapRequest(BaseModel):
    replacement_type: str = Field(
        pattern="^(hotel|accommodation|restaurant|dining|food|attraction|activity|transport|transportation)$",
        description="Type of catalogue entity being selected",
    )
    replacement_id: int = Field(gt=0, description="Catalogue entity ID from destinations catalogue")
    title: Optional[str] = Field(default=None, max_length=180, description="Optional custom title override")


class ItineraryDayResponse(BaseModel):
    id: int
    itinerary_id: int
    day_number: int
    itinerary_date: date
    items: List[ItineraryItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ItineraryDetailResponse(BaseModel):
    id: int
    trip_id: int
    version: int
    summary: str
    provider: str
    created_at: datetime
    days: List[ItineraryDayResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# BUDGET & ALLOCATIONS
# ============================================================================


class BudgetAllocationResponse(BaseModel):
    id: Optional[int] = None
    trip_id: int
    category: str
    amount: Decimal

    model_config = ConfigDict(from_attributes=True)


class BudgetSummaryResponse(BaseModel):
    total_budget: Decimal
    estimated_total: Decimal
    remaining_budget: Decimal
    deficit: Decimal
    utilization_percentage: Decimal
    status: str  # 'within_budget', 'exact', 'over_budget'
    categories: List[BudgetAllocationResponse] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# ============================================================================
# TRIP REQUESTS & RESPONSES
# ============================================================================


class TripCreateRequest(BaseModel):
    destination_id: int = Field(gt=0, description="Destination ID from catalogue")
    starting_location: str = Field(min_length=2, max_length=120, description="Starting city or station")
    start_date: date
    end_date: date
    traveller_count: int = Field(default=1, gt=0, le=50, description="Number of travellers")
    total_budget: Decimal = Field(gt=0, max_digits=12, decimal_places=2, description="Total budget in currency")
    preferences: Optional[List[str]] = Field(default_factory=list, description="Travel style preferences")
    members: Optional[List[TripMemberCreateRequest]] = Field(default_factory=list)
    generate_plan: bool = Field(default=False, description="Automatically generate and persist initial plan")

    @model_validator(mode="after")
    def validate_dates(self) -> "TripCreateRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if (self.end_date - self.start_date).days > 30:
            raise ValueError("Trip duration cannot exceed 31 days")
        return self


class TripUpdateRequest(BaseModel):
    destination_id: Optional[int] = Field(default=None, gt=0)
    starting_location: Optional[str] = Field(default=None, min_length=2, max_length=120)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    traveller_count: Optional[int] = Field(default=None, gt=0, le=50)
    total_budget: Optional[Decimal] = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    status: Optional[str] = Field(default=None, pattern="^(draft|planned|completed|cancelled)$")

    @model_validator(mode="after")
    def validate_dates(self) -> "TripUpdateRequest":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if self.start_date and self.end_date and (self.end_date - self.start_date).days > 30:
            raise ValueError("Trip duration cannot exceed 31 days")
        return self


class TripSummaryResponse(BaseModel):
    id: int
    user_id: int
    destination_id: int
    destination_city: Optional[str] = None
    destination_country: Optional[str] = None
    starting_location: str
    start_date: date
    end_date: date
    traveller_count: int
    total_budget: Decimal
    estimated_total: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TripDetailResponse(BaseModel):
    id: int
    user_id: int
    destination_id: int
    destination_city: Optional[str] = None
    destination_country: Optional[str] = None
    starting_location: str
    start_date: date
    end_date: date
    traveller_count: int
    total_budget: Decimal
    estimated_total: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    members: List[TripMemberResponse] = Field(default_factory=list)
    itineraries: List[ItineraryDetailResponse] = Field(default_factory=list)
    budget_allocations: List[BudgetAllocationResponse] = Field(default_factory=list)
    budget_summary: Optional[BudgetSummaryResponse] = None
    packing_items: List[PackingItemResponse] = Field(default_factory=list)
    is_saved: bool = False

    model_config = ConfigDict(from_attributes=True)


class TripPlanGenerateResponse(BaseModel):
    trip: TripDetailResponse
    itinerary: ItineraryDetailResponse
    budget_summary: BudgetSummaryResponse
    optimization_applied: bool
    warnings: List[str] = Field(default_factory=list)


class SavedTripResponse(BaseModel):
    id: int
    user_id: int
    trip_id: int
    saved_at: datetime
    trip: Optional[TripSummaryResponse] = None

    model_config = ConfigDict(from_attributes=True)
