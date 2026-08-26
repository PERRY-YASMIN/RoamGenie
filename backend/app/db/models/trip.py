from datetime import date, datetime, time
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.ai import AIConversation
    from app.db.models.catalogue import Destination
    from app.db.models.finance import BudgetAllocation, Expense, SavedTrip
    from app.db.models.user import User


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    destination_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("destinations.id"),
        nullable=False,
        index=True,
    )
    starting_location: Mapped[str] = mapped_column(String(120), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    traveller_count: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("traveller_count > 0", name="check_trip_travellers"),
        nullable=False,
    )
    total_budget: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("total_budget > 0", name="check_trip_budget"),
        nullable=False,
    )
    estimated_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("estimated_total >= 0", name="check_trip_est_total"),
        nullable=False,
        default=Decimal("0.00"),
    )
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("status IN ('draft', 'planned', 'completed', 'cancelled')", name="check_trip_status"),
        nullable=False,
        default="draft",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="check_trip_dates"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="trips")
    destination: Mapped["Destination"] = relationship("Destination", back_populates="trips")
    members: Mapped[List["TripMember"]] = relationship(
        "TripMember", back_populates="trip", cascade="all, delete-orphan"
    )
    itineraries: Mapped[List["Itinerary"]] = relationship(
        "Itinerary", back_populates="trip", cascade="all, delete-orphan"
    )
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense", back_populates="trip", cascade="all, delete-orphan"
    )
    budget_allocations: Mapped[List["BudgetAllocation"]] = relationship(
        "BudgetAllocation", back_populates="trip", cascade="all, delete-orphan"
    )
    saved_trips: Mapped[List["SavedTrip"]] = relationship(
        "SavedTrip", back_populates="trip", cascade="all, delete-orphan"
    )
    packing_items: Mapped[List["PackingItem"]] = relationship(
        "PackingItem", back_populates="trip", cascade="all, delete-orphan"
    )
    ai_conversations: Mapped[List["AIConversation"]] = relationship(
        "AIConversation", back_populates="trip"
    )


class TripMember(Base):
    __tablename__ = "trip_members"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    trip_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    age_group: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    special_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    trip: Mapped["Trip"] = relationship("Trip", back_populates="members")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    trip_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("version > 0", name="check_itinerary_version"),
        nullable=False,
        default=1,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    provider: Mapped[str] = mapped_column(String(40), nullable=False, default="mock")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("trip_id", "version", name="uq_itineraries_trip_version"),
    )

    trip: Mapped["Trip"] = relationship("Trip", back_populates="itineraries")
    days: Mapped[List["ItineraryDay"]] = relationship(
        "ItineraryDay", back_populates="itinerary", cascade="all, delete-orphan"
    )


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    itinerary_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("itineraries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_number: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("day_number > 0", name="check_day_number"),
        nullable=False,
    )
    itinerary_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("itinerary_id", "day_number", name="uq_itinerary_days_itinerary_day"),
    )

    itinerary: Mapped["Itinerary"] = relationship("Itinerary", back_populates="days")
    items: Mapped[List["ItineraryItem"]] = relationship(
        "ItineraryItem", back_populates="day", cascade="all, delete-orphan"
    )


class ItineraryItem(Base):
    __tablename__ = "itinerary_items"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    itinerary_day_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("itinerary_days.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_order: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("item_order > 0", name="check_item_order"),
        nullable=False,
    )
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    estimated_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        CheckConstraint("estimated_cost >= 0", name="check_item_cost"),
        nullable=False,
        default=Decimal("0.00"),
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("itinerary_day_id", "item_order", name="uq_itinerary_items_day_order"),
    )

    day: Mapped["ItineraryDay"] = relationship("ItineraryDay", back_populates="items")


class PackingItem(Base):
    __tablename__ = "packing_items"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    trip_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    is_packed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("trip_id", "item", name="uq_packing_items_trip_item"),
    )

    trip: Mapped["Trip"] = relationship("Trip", back_populates="packing_items")
