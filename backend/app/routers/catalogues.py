from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.catalogue import (
    Attraction,
    Destination,
    Hotel,
    Restaurant,
    TransportOption,
)
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.catalogue import (
    AttractionCreateRequest,
    AttractionResponse,
    DestinationCreateRequest,
    DestinationResponse,
    HotelCreateRequest,
    HotelResponse,
    RestaurantCreateRequest,
    RestaurantResponse,
    TransportOptionCreateRequest,
    TransportOptionResponse,
)
from app.schemas.weather import DestinationWeatherResponse
from app.services.auth_service import get_current_admin
from app.services.weather_service import WeatherService, get_weather_service

router = APIRouter(tags=["catalogues"])


# ============================================================================
# DESTINATIONS
# ============================================================================


@router.get("/destinations", response_model=List[DestinationResponse])
def list_destinations(
    search: Optional[str] = Query(None, description="Search by city or country"),
    active_only: bool = Query(True, description="Filter only active destinations"),
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> List[DestinationResponse]:
    """Browse and search travel destinations."""
    stmt = select(Destination)
    if active_only:
        stmt = stmt.where(Destination.active == True)  # noqa: E712
    if search:
        pattern = f"%{search.strip().lower()}%"
        stmt = stmt.where(
            func.lower(Destination.city).like(pattern)
            | func.lower(Destination.country).like(pattern)
        )
    stmt = stmt.order_by(Destination.city).offset(skip).limit(limit)
    results = db.execute(stmt).scalars().all()
    return [DestinationResponse.model_validate(d) for d in results]


@router.get("/destinations/{destination_id}", response_model=DestinationResponse)
def get_destination(
    destination_id: int, db: Session = Depends(get_db)
) -> DestinationResponse:
    """Retrieve details for a specific destination."""
    dest = db.get(Destination, destination_id)
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found."
        )
    return DestinationResponse.model_validate(dest)


@router.get("/destinations/{destination_id}/weather", response_model=DestinationWeatherResponse)
def get_destination_weather(
    destination_id: int,
    db: Session = Depends(get_db),
    weather_service: WeatherService = Depends(get_weather_service),
) -> DestinationWeatherResponse:
    """Retrieve live / normalized weather forecast for a destination."""
    dest = db.get(Destination, destination_id)
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found."
        )
    return weather_service.get_destination_weather(db=db, destination=dest)


@router.post(
    "/destinations",
    response_model=DestinationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_destination(
    request: DestinationCreateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> DestinationResponse:
    """Admin-only: Add a new destination."""
    stmt = select(Destination).where(
        Destination.city == request.city, Destination.country == request.country
    )
    if db.execute(stmt).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Destination already exists for this city and country.",
        )
    dest = Destination(**request.model_dump())
    db.add(dest)
    db.commit()
    db.refresh(dest)
    return DestinationResponse.model_validate(dest)


# ============================================================================
# HOTELS
# ============================================================================


@router.get("/hotels", response_model=List[HotelResponse])
def list_hotels(
    destination_id: Optional[int] = Query(None, description="Filter by destination ID"),
    max_price: Optional[Decimal] = Query(None, ge=0, description="Max price per night"),
    min_rating: Optional[Decimal] = Query(None, ge=0, le=5, description="Min rating"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[HotelResponse]:
    """Browse accommodations with optional filters."""
    stmt = select(Hotel)
    if destination_id:
        stmt = stmt.where(Hotel.destination_id == destination_id)
    if max_price is not None:
        stmt = stmt.where(Hotel.price_per_night <= max_price)
    if min_rating is not None:
        stmt = stmt.where(Hotel.rating >= min_rating)
    stmt = stmt.order_by(Hotel.price_per_night).offset(skip).limit(limit)
    hotels = db.execute(stmt).scalars().all()
    return [HotelResponse.model_validate(h) for h in hotels]


@router.post(
    "/hotels",
    response_model=HotelResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hotel(
    request: HotelCreateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> HotelResponse:
    """Admin-only: Add a new hotel."""
    if not db.get(Destination, request.destination_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found."
        )
    hotel = Hotel(**request.model_dump())
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    return HotelResponse.model_validate(hotel)


# ============================================================================
# RESTAURANTS
# ============================================================================


@router.get("/restaurants", response_model=List[RestaurantResponse])
def list_restaurants(
    destination_id: Optional[int] = Query(None, description="Filter by destination ID"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    max_cost: Optional[Decimal] = Query(None, ge=0, description="Max cost per person"),
    min_rating: Optional[Decimal] = Query(None, ge=0, le=5, description="Min rating"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[RestaurantResponse]:
    """Browse dining options with optional filters."""
    stmt = select(Restaurant)
    if destination_id:
        stmt = stmt.where(Restaurant.destination_id == destination_id)
    if cuisine:
        stmt = stmt.where(func.lower(Restaurant.cuisine).like(f"%{cuisine.strip().lower()}%"))
    if max_cost is not None:
        stmt = stmt.where(Restaurant.average_cost_per_person <= max_cost)
    if min_rating is not None:
        stmt = stmt.where(Restaurant.rating >= min_rating)
    stmt = stmt.order_by(Restaurant.name).offset(skip).limit(limit)
    restaurants = db.execute(stmt).scalars().all()
    return [RestaurantResponse.model_validate(r) for r in restaurants]


@router.post(
    "/restaurants",
    response_model=RestaurantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_restaurant(
    request: RestaurantCreateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> RestaurantResponse:
    """Admin-only: Add a new restaurant."""
    if not db.get(Destination, request.destination_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found."
        )
    restaurant = Restaurant(**request.model_dump())
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return RestaurantResponse.model_validate(restaurant)


# ============================================================================
# ATTRACTIONS
# ============================================================================


@router.get("/attractions", response_model=List[AttractionResponse])
def list_attractions(
    destination_id: Optional[int] = Query(None, description="Filter by destination ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    max_fee: Optional[Decimal] = Query(None, ge=0, description="Max entry fee"),
    min_rating: Optional[Decimal] = Query(None, ge=0, le=5, description="Min rating"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[AttractionResponse]:
    """Browse attractions with optional category and fee filters."""
    stmt = select(Attraction)
    if destination_id:
        stmt = stmt.where(Attraction.destination_id == destination_id)
    if category:
        stmt = stmt.where(func.lower(Attraction.category) == category.strip().lower())
    if max_fee is not None:
        stmt = stmt.where(Attraction.entry_fee <= max_fee)
    if min_rating is not None:
        stmt = stmt.where(Attraction.rating >= min_rating)
    stmt = stmt.order_by(Attraction.name).offset(skip).limit(limit)
    attractions = db.execute(stmt).scalars().all()
    return [AttractionResponse.model_validate(a) for a in attractions]


@router.post(
    "/attractions",
    response_model=AttractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_attraction(
    request: AttractionCreateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AttractionResponse:
    """Admin-only: Add a new attraction."""
    if not db.get(Destination, request.destination_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found."
        )
    attraction = Attraction(**request.model_dump())
    db.add(attraction)
    db.commit()
    db.refresh(attraction)
    return AttractionResponse.model_validate(attraction)


# ============================================================================
# TRANSPORT OPTIONS
# ============================================================================


@router.get("/transport-options", response_model=List[TransportOptionResponse])
def list_transport_options(
    origin: Optional[str] = Query(None, description="Filter by origin city"),
    destination_id: Optional[int] = Query(None, description="Filter by destination ID"),
    mode: Optional[str] = Query(None, description="Filter by mode (train, bus, flight, car)"),
    max_cost: Optional[Decimal] = Query(None, ge=0, description="Max cost"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[TransportOptionResponse]:
    """Browse transportation options between origins and destinations."""
    stmt = select(TransportOption)
    if origin:
        stmt = stmt.where(func.lower(TransportOption.origin) == origin.strip().lower())
    if destination_id:
        stmt = stmt.where(TransportOption.destination_id == destination_id)
    if mode:
        stmt = stmt.where(func.lower(TransportOption.mode) == mode.strip().lower())
    if max_cost is not None:
        stmt = stmt.where(TransportOption.estimated_cost <= max_cost)
    stmt = stmt.order_by(TransportOption.estimated_cost).offset(skip).limit(limit)
    transports = db.execute(stmt).scalars().all()
    return [TransportOptionResponse.model_validate(t) for t in transports]


@router.post(
    "/transport-options",
    response_model=TransportOptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transport_option(
    request: TransportOptionCreateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> TransportOptionResponse:
    """Admin-only: Add a new transport option."""
    if not db.get(Destination, request.destination_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found."
        )
    transport = TransportOption(**request.model_dump())
    db.add(transport)
    db.commit()
    db.refresh(transport)
    return TransportOptionResponse.model_validate(transport)
