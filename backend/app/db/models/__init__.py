from app.db.base import Base
from app.db.models.ai import AIConversation, AIMessage, TripAudit, WeatherSnapshot
from app.db.models.catalogue import (
    Attraction,
    Destination,
    Hotel,
    Restaurant,
    TransportOption,
)
from app.db.models.finance import BudgetAllocation, Expense, Review, SavedTrip
from app.db.models.trip import (
    Itinerary,
    ItineraryDay,
    ItineraryItem,
    PackingItem,
    Trip,
    TripMember,
)
from app.db.models.user import ActivityPreference, User, UserPreference

__all__ = [
    "Base",
    "User",
    "UserPreference",
    "ActivityPreference",
    "Destination",
    "Hotel",
    "Restaurant",
    "Attraction",
    "TransportOption",
    "Trip",
    "TripMember",
    "Itinerary",
    "ItineraryDay",
    "ItineraryItem",
    "PackingItem",
    "Expense",
    "BudgetAllocation",
    "SavedTrip",
    "Review",
    "AIConversation",
    "AIMessage",
    "WeatherSnapshot",
    "TripAudit",
]
