from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.ai import AIConversation
    from app.db.models.finance import Review, SavedTrip
    from app.db.models.trip import Trip


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
        autoincrement=True,
    )
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("role IN ('traveller', 'admin')", name="check_user_role"),
        nullable=False,
        default="traveller",
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

    # Relationships
    preference: Mapped[Optional["UserPreference"]] = relationship(
        "UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    activity_preferences: Mapped[List["ActivityPreference"]] = relationship(
        "ActivityPreference", back_populates="user", cascade="all, delete-orphan"
    )
    trips: Mapped[List["Trip"]] = relationship(
        "Trip", back_populates="user", cascade="all, delete-orphan"
    )
    saved_trips: Mapped[List["SavedTrip"]] = relationship(
        "SavedTrip", back_populates="user", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="user", cascade="all, delete-orphan"
    )
    ai_conversations: Mapped[List["AIConversation"]] = relationship(
        "AIConversation", back_populates="user", cascade="all, delete-orphan"
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    hotel_preference: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    food_preference: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    transport_preference: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    travel_style: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    special_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="preference")


class ActivityPreference(Base):
    __tablename__ = "activity_preferences"

    user_id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    activity: Mapped[str] = mapped_column(String(60), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="activity_preferences")
