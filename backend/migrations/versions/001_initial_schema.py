"""create initial travel schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-20 10:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=20), server_default="traveller", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("role IN ('traveller', 'admin')", name="check_user_role"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # 2. user_preferences
    op.create_table(
        "user_preferences",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("hotel_preference", sa.String(length=40), nullable=True),
        sa.Column("food_preference", sa.String(length=80), nullable=True),
        sa.Column("transport_preference", sa.String(length=40), nullable=True),
        sa.Column("travel_style", sa.String(length=40), nullable=True),
        sa.Column("special_requirements", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    # 3. activity_preferences
    op.create_table(
        "activity_preferences",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("activity", sa.String(length=60), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "activity"),
    )

    # 4. destinations
    op.create_table(
        "destinations",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("average_daily_cost", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.CheckConstraint("average_daily_cost >= 0", name="check_dest_daily_cost"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("city", "country", name="uq_destinations_city_country"),
    )
    op.create_index(op.f("ix_destinations_city"), "destinations", ["city"], unique=False)
    op.create_index(op.f("ix_destinations_country"), "destinations", ["country"], unique=False)

    # 5. hotels
    op.create_table(
        "hotels",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("destination_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("price_per_night", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("rating", sa.Numeric(precision=2, scale=1), nullable=True),
        sa.CheckConstraint("price_per_night >= 0", name="check_hotel_price"),
        sa.CheckConstraint("rating >= 0 AND rating <= 5", name="check_hotel_rating"),
        sa.ForeignKeyConstraint(["destination_id"], ["destinations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("destination_id", "name", name="uq_hotels_dest_name"),
    )
    op.create_index(op.f("ix_hotels_destination_id"), "hotels", ["destination_id"], unique=False)

    # 6. restaurants
    op.create_table(
        "restaurants",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("destination_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("cuisine", sa.String(length=80), nullable=True),
        sa.Column("average_cost_per_person", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("rating", sa.Numeric(precision=2, scale=1), nullable=True),
        sa.CheckConstraint("average_cost_per_person >= 0", name="check_restaurant_cost"),
        sa.CheckConstraint("rating >= 0 AND rating <= 5", name="check_restaurant_rating"),
        sa.ForeignKeyConstraint(["destination_id"], ["destinations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("destination_id", "name", name="uq_restaurants_dest_name"),
    )
    op.create_index(op.f("ix_restaurants_destination_id"), "restaurants", ["destination_id"], unique=False)

    # 7. attractions
    op.create_table(
        "attractions",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("destination_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=True),
        sa.Column("entry_fee", sa.Numeric(precision=12, scale=2), server_default="0", nullable=False),
        sa.Column("rating", sa.Numeric(precision=2, scale=1), nullable=True),
        sa.CheckConstraint("entry_fee >= 0", name="check_attraction_fee"),
        sa.CheckConstraint("rating >= 0 AND rating <= 5", name="check_attraction_rating"),
        sa.ForeignKeyConstraint(["destination_id"], ["destinations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("destination_id", "name", name="uq_attractions_dest_name"),
    )
    op.create_index(op.f("ix_attractions_category"), "attractions", ["category"], unique=False)
    op.create_index(op.f("ix_attractions_destination_id"), "attractions", ["destination_id"], unique=False)

    # 8. transport_options
    op.create_table(
        "transport_options",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("origin", sa.String(length=100), nullable=False),
        sa.Column("destination_id", sa.BigInteger(), nullable=False),
        sa.Column("mode", sa.String(length=40), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=True),
        sa.Column("estimated_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.CheckConstraint("estimated_cost >= 0", name="check_transport_cost"),
        sa.CheckConstraint("duration_minutes > 0", name="check_transport_duration"),
        sa.ForeignKeyConstraint(["destination_id"], ["destinations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_transport_options_destination_id"), "transport_options", ["destination_id"], unique=False)
    op.create_index(op.f("ix_transport_options_origin"), "transport_options", ["origin"], unique=False)

    # 9. trips
    op.create_table(
        "trips",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("destination_id", sa.BigInteger(), nullable=False),
        sa.Column("starting_location", sa.String(length=120), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("traveller_count", sa.Integer(), nullable=False),
        sa.Column("total_budget", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("estimated_total", sa.Numeric(precision=12, scale=2), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("end_date >= start_date", name="check_trip_dates"),
        sa.CheckConstraint("estimated_total >= 0", name="check_trip_est_total"),
        sa.CheckConstraint("status IN ('draft', 'planned', 'completed', 'cancelled')", name="check_trip_status"),
        sa.CheckConstraint("total_budget > 0", name="check_trip_budget"),
        sa.CheckConstraint("traveller_count > 0", name="check_trip_travellers"),
        sa.ForeignKeyConstraint(["destination_id"], ["destinations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trips_destination_id"), "trips", ["destination_id"], unique=False)
    op.create_index(op.f("ix_trips_start_date"), "trips", ["start_date"], unique=False)
    op.create_index(op.f("ix_trips_user_id"), "trips", ["user_id"], unique=False)

    # 10. trip_members
    op.create_table(
        "trip_members",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("age_group", sa.String(length=30), nullable=True),
        sa.Column("special_requirements", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trip_members_trip_id"), "trip_members", ["trip_id"], unique=False)

    # 11. itineraries
    op.create_table(
        "itineraries",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("summary", sa.Text(), server_default="", nullable=False),
        sa.Column("provider", sa.String(length=40), server_default="mock", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("version > 0", name="check_itinerary_version"),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trip_id", "version", name="uq_itineraries_trip_version"),
    )
    op.create_index(op.f("ix_itineraries_trip_id"), "itineraries", ["trip_id"], unique=False)

    # 12. itinerary_days
    op.create_table(
        "itinerary_days",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("itinerary_id", sa.BigInteger(), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("itinerary_date", sa.Date(), nullable=False),
        sa.CheckConstraint("day_number > 0", name="check_day_number"),
        sa.ForeignKeyConstraint(["itinerary_id"], ["itineraries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("itinerary_id", "day_number", name="uq_itinerary_days_itinerary_day"),
    )
    op.create_index(op.f("ix_itinerary_days_itinerary_id"), "itinerary_days", ["itinerary_id"], unique=False)

    # 13. itinerary_items
    op.create_table(
        "itinerary_items",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("itinerary_day_id", sa.BigInteger(), nullable=False),
        sa.Column("item_order", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("estimated_cost", sa.Numeric(precision=12, scale=2), server_default="0", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint("estimated_cost >= 0", name="check_item_cost"),
        sa.CheckConstraint("item_order > 0", name="check_item_order"),
        sa.ForeignKeyConstraint(["itinerary_day_id"], ["itinerary_days.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("itinerary_day_id", "item_order", name="uq_itinerary_items_day_order"),
    )
    op.create_index(op.f("ix_itinerary_items_itinerary_day_id"), "itinerary_items", ["itinerary_day_id"], unique=False)

    # 14. expenses
    op.create_table(
        "expenses",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("incurred_on", sa.Date(), nullable=True),
        sa.CheckConstraint("amount >= 0", name="check_expense_amount"),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_expenses_category"), "expenses", ["category"], unique=False)
    op.create_index(op.f("ix_expenses_trip_id"), "expenses", ["trip_id"], unique=False)

    # 15. budget_allocations
    op.create_table(
        "budget_allocations",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.CheckConstraint("amount >= 0", name="check_allocation_amount"),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trip_id", "category", name="uq_budget_allocations_trip_category"),
    )
    op.create_index(op.f("ix_budget_allocations_trip_id"), "budget_allocations", ["trip_id"], unique=False)

    # 16. saved_trips
    op.create_table(
        "saved_trips",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "trip_id", name="uq_saved_trips_user_trip"),
    )
    op.create_index(op.f("ix_saved_trips_trip_id"), "saved_trips", ["trip_id"], unique=False)
    op.create_index(op.f("ix_saved_trips_user_id"), "saved_trips", ["user_id"], unique=False)

    # 17. reviews
    op.create_table(
        "reviews",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("destination_id", sa.BigInteger(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="check_review_rating"),
        sa.ForeignKeyConstraint(["destination_id"], ["destinations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "destination_id", name="uq_reviews_user_dest"),
    )
    op.create_index(op.f("ix_reviews_destination_id"), "reviews", ["destination_id"], unique=False)
    op.create_index(op.f("ix_reviews_user_id"), "reviews", ["user_id"], unique=False)

    # 18. ai_conversations
    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_conversations_trip_id"), "ai_conversations", ["trip_id"], unique=False)
    op.create_index(op.f("ix_ai_conversations_user_id"), "ai_conversations", ["user_id"], unique=False)

    # 19. ai_messages
    op.create_table(
        "ai_messages",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("conversation_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name="check_ai_msg_role"),
        sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_messages_conversation_id"), "ai_messages", ["conversation_id"], unique=False)

    # 20. weather_snapshots
    op.create_table(
        "weather_snapshots",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("destination_id", sa.BigInteger(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.String(length=160), nullable=False),
        sa.Column("temperature_c", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("provider", sa.String(length=40), server_default="mock", nullable=False),
        sa.ForeignKeyConstraint(["destination_id"], ["destinations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_weather_snapshots_destination_id"), "weather_snapshots", ["destination_id"], unique=False)
    op.create_index(op.f("ix_weather_snapshots_observed_at"), "weather_snapshots", ["observed_at"], unique=False)

    # 21. packing_items
    op.create_table(
        "packing_items",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=False),
        sa.Column("item", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=True),
        sa.Column("is_packed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trip_id", "item", name="uq_packing_items_trip_item"),
    )
    op.create_index(op.f("ix_packing_items_trip_id"), "packing_items", ["trip_id"], unique=False)

    # 22. trip_audit
    op.create_table(
        "trip_audit",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=True), nullable=False),
        sa.Column("trip_id", sa.BigInteger(), nullable=True),
        sa.Column("action", sa.String(length=10), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changed_by", sa.Text(), server_default=sa.text("CURRENT_USER"), nullable=False),
        sa.Column("old_row", sa.JSON(), nullable=True),
        sa.Column("new_row", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trip_audit_trip_id"), "trip_audit", ["trip_id"], unique=False)


def downgrade() -> None:
    op.drop_table("trip_audit")
    op.drop_table("packing_items")
    op.drop_table("weather_snapshots")
    op.drop_table("ai_messages")
    op.drop_table("ai_conversations")
    op.drop_table("reviews")
    op.drop_table("saved_trips")
    op.drop_table("budget_allocations")
    op.drop_table("expenses")
    op.drop_table("itinerary_items")
    op.drop_table("itinerary_days")
    op.drop_table("itineraries")
    op.drop_table("trip_members")
    op.drop_table("trips")
    op.drop_table("transport_options")
    op.drop_table("attractions")
    op.drop_table("restaurants")
    op.drop_table("hotels")
    op.drop_table("destinations")
    op.drop_table("activity_preferences")
    op.drop_table("user_preferences")
    op.drop_table("users")
