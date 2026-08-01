from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class TripPlanRequest(BaseModel):
    starting_location: str = Field(min_length=2, max_length=120)
    destination: str = Field(min_length=2, max_length=120)
    start_date: date
    end_date: date
    travellers: int = Field(gt=0, le=50)
    total_budget: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    preferences: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def dates_are_ordered(self) -> "TripPlanRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if (self.end_date - self.start_date).days > 30:
            raise ValueError("starter supports trips of at most 31 days")
        return self


class ItineraryItem(BaseModel):
    time: str
    title: str
    category: str
    estimated_cost: Decimal = Field(ge=0)


class ItineraryDay(BaseModel):
    day_number: int = Field(gt=0)
    date: date
    items: list[ItineraryItem]


class BudgetCategory(BaseModel):
    category: str
    amount: Decimal = Field(ge=0)


class ItineraryProposal(BaseModel):
    provider: str
    summary: str
    days: list[ItineraryDay]
    budget_split: list[BudgetCategory]
    estimated_total: Decimal = Field(ge=0)
    remaining_budget: Decimal
    warnings: list[str]
    packing_items: list[str]

