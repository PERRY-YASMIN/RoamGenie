from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AITripItem(BaseModel):
    time: str = Field(pattern=r"^\d{1,2}:\d{2}$", description="Time in HH:MM format")
    title: str = Field(min_length=2, max_length=180)
    category: str = Field(description="One of: transportation, accommodation, food, attractions")
    estimated_cost: Decimal = Field(ge=0, description="Estimated cost in INR")
    notes: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class AITripDay(BaseModel):
    day_number: int = Field(gt=0)
    date: date
    items: List[AITripItem] = Field(min_length=1)

    model_config = ConfigDict(from_attributes=True)


class AIBudgetSplit(BaseModel):
    category: str
    amount: Decimal = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)


class AIItineraryOutput(BaseModel):
    summary: str = Field(min_length=5, max_length=500)
    days: List[AITripDay] = Field(min_length=1)
    budget_split: List[AIBudgetSplit] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    packing_items: List[str] = Field(default_factory=list)
    weather_advice: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
