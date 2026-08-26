from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.ai import WeatherSnapshot
    from app.db.models.finance import Review
    from app.db.models.trip import Trip


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    average_daily_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("average_daily_cost >= 0", name="check_dest_daily_cost"),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("city", "country", name="uq_destinations_city_country"),
    )

    # Relationships
    hotels: Mapped[List["Hotel"]] = relationship(
        "Hotel", back_populates="destination", cascade="all, delete-orphan"
    )
    restaurants: Mapped[List["Restaurant"]] = relationship(
        "Restaurant", back_populates="destination", cascade="all, delete-orphan"
    )
    attractions: Mapped[List["Attraction"]] = relationship(
        "Attraction", back_populates="destination", cascade="all, delete-orphan"
    )
    transport_options: Mapped[List["TransportOption"]] = relationship(
        "TransportOption", back_populates="destination", cascade="all, delete-orphan"
    )
    trips: Mapped[List["Trip"]] = relationship("Trip", back_populates="destination")
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="destination", cascade="all, delete-orphan"
    )
    weather_snapshots: Mapped[List["WeatherSnapshot"]] = relationship(
        "WeatherSnapshot", back_populates="destination", cascade="all, delete-orphan"
    )


class Hotel(Base):
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    destination_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    price_per_night: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("price_per_night >= 0", name="check_hotel_price"),
        nullable=False,
    )
    rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1),
        CheckConstraint("rating >= 0 AND rating <= 5", name="check_hotel_rating"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("destination_id", "name", name="uq_hotels_dest_name"),
    )

    destination: Mapped["Destination"] = relationship("Destination", back_populates="hotels")


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    destination_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    cuisine: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    average_cost_per_person: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("average_cost_per_person >= 0", name="check_restaurant_cost"),
        nullable=True,
    )
    rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1),
        CheckConstraint("rating >= 0 AND rating <= 5", name="check_restaurant_rating"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("destination_id", "name", name="uq_restaurants_dest_name"),
    )

    destination: Mapped["Destination"] = relationship("Destination", back_populates="restaurants")


class Attraction(Base):
    __tablename__ = "attractions"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    destination_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(60), nullable=True, index=True)
    entry_fee: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("entry_fee >= 0", name="check_attraction_fee"),
        nullable=False,
        default=Decimal("0.00"),
    )
    rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1),
        CheckConstraint("rating >= 0 AND rating <= 5", name="check_attraction_rating"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("destination_id", "name", name="uq_attractions_dest_name"),
    )

    destination: Mapped["Destination"] = relationship("Destination", back_populates="attractions")


class TransportOption(Base):
    __tablename__ = "transport_options"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    origin: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    destination_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("destinations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mode: Mapped[str] = mapped_column(String(40), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estimated_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("estimated_cost >= 0", name="check_transport_cost"),
        nullable=False,
    )
    duration_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("duration_minutes > 0", name="check_transport_duration"),
        nullable=True,
    )

    destination: Mapped["Destination"] = relationship("Destination", back_populates="transport_options")
