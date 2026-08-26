from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# --- Destinations ---
class DestinationBase(BaseModel):
    city: str = Field(min_length=2, max_length=100)
    country: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=1000)
    average_daily_cost: Optional[Decimal] = Field(default=None, ge=0)
    active: bool = True


class DestinationCreateRequest(DestinationBase):
    pass


class DestinationResponse(DestinationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Hotels ---
class HotelBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    price_per_night: Decimal = Field(ge=0)
    rating: Optional[Decimal] = Field(default=None, ge=0, le=5)


class HotelCreateRequest(HotelBase):
    destination_id: int


class HotelResponse(HotelBase):
    id: int
    destination_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Restaurants ---
class RestaurantBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    cuisine: Optional[str] = Field(default=None, max_length=80)
    average_cost_per_person: Optional[Decimal] = Field(default=None, ge=0)
    rating: Optional[Decimal] = Field(default=None, ge=0, le=5)


class RestaurantCreateRequest(RestaurantBase):
    destination_id: int


class RestaurantResponse(RestaurantBase):
    id: int
    destination_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Attractions ---
class AttractionBase(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    category: Optional[str] = Field(default=None, max_length=60)
    entry_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    rating: Optional[Decimal] = Field(default=None, ge=0, le=5)


class AttractionCreateRequest(AttractionBase):
    destination_id: int


class AttractionResponse(AttractionBase):
    id: int
    destination_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Transport Options ---
class TransportOptionBase(BaseModel):
    origin: str = Field(min_length=2, max_length=100)
    mode: str = Field(min_length=2, max_length=40)
    provider: Optional[str] = Field(default=None, max_length=100)
    estimated_cost: Decimal = Field(ge=0)
    duration_minutes: Optional[int] = Field(default=None, gt=0)


class TransportOptionCreateRequest(TransportOptionBase):
    destination_id: int


class TransportOptionResponse(TransportOptionBase):
    id: int
    destination_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Paginated Catalogue Envelope ---
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[dict]
