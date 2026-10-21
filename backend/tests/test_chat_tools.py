from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.catalogue import Destination, Hotel, Restaurant, Attraction, TransportOption
from app.db.models.trip import Trip, Itinerary, ItineraryDay, ItineraryItem
from app.db.models.user import User
from app.services.ai_providers import GeminiLLMProvider, LLMResponse
from app.services.chat_tools import (
    execute_chat_tool,
    get_itinerary_details,
    get_travel_history,
    propose_itinerary_modification,
)


@pytest.fixture
def tool_destination(db_session: Session) -> Destination:
    dest = Destination(
        city="Kochi",
        country="India",
        description="Queen of the Arabian Sea",
        average_daily_cost=Decimal("3500.00"),
        active=True,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)

    h1 = Hotel(destination_id=dest.id, name="Luxury Fort Resort", price_per_night=Decimal("5000.00"), rating=Decimal("4.8"))
    h2 = Hotel(destination_id=dest.id, name="Budget Heritage Stay", price_per_night=Decimal("2000.00"), rating=Decimal("4.2"))
    r1 = Restaurant(destination_id=dest.id, name="Malabar Seafood", cuisine="Kerala", average_cost_per_person=Decimal("400.00"))
    a1 = Attraction(destination_id=dest.id, name="Chinese Fishing Nets", category="sightseeing", entry_fee=Decimal("50.00"))

    db_session.add_all([h1, h2, r1, a1])
    db_session.commit()
    return dest


@pytest.fixture
def user_trip(db_session: Session, tool_destination: Destination) -> Trip:
    # User ID 1 is traveller in test database
    trip = Trip(
        user_id=1,
        destination_id=tool_destination.id,
        starting_location="Bangalore",
        start_date=date.today() + timedelta(days=5),
        end_date=date.today() + timedelta(days=6),
        traveller_count=2,
        total_budget=Decimal("15000.00"),
        estimated_total=Decimal("5800.00"),
        status="planned",
    )
    db_session.add(trip)
    db_session.commit()
    db_session.refresh(trip)

    itin = Itinerary(trip_id=trip.id, version=1, summary="Coastal Getaway", provider="test")
    db_session.add(itin)
    db_session.commit()
    db_session.refresh(itin)

    day1 = ItineraryDay(itinerary_id=itin.id, day_number=1, itinerary_date=trip.start_date)
    day2 = ItineraryDay(itinerary_id=itin.id, day_number=2, itinerary_date=trip.end_date)
    db_session.add_all([day1, day2])
    db_session.commit()
    db_session.refresh(day1)

    item1 = ItineraryItem(
        itinerary_day_id=day1.id,
        item_order=1,
        title="Stay at Luxury Fort Resort",
        category="accommodation",
        estimated_cost=Decimal("5000.00"),
    )
    item2 = ItineraryItem(
        itinerary_day_id=day1.id,
        item_order=2,
        title="Dinner at Malabar Seafood",
        category="food",
        estimated_cost=Decimal("800.00"),
    )
    db_session.add_all([item1, item2])
    db_session.commit()
    db_session.refresh(item1)
    db_session.refresh(item2)

    return trip


def test_tool_get_travel_history(db_session: Session, user_trip: Trip):
    """Verify get_travel_history retrieves strictly user-owned trips."""
    # User 1 history
    res = get_travel_history(db=db_session, user_id=1)
    assert res["total_trips"] >= 1
    assert any(t["id"] == user_trip.id for t in res["trips"])

    # User 999 (different user) has 0 trips
    res_other = get_travel_history(db=db_session, user_id=999)
    assert res_other["total_trips"] == 0


def test_tool_get_itinerary_details(db_session: Session, user_trip: Trip):
    """Verify get_itinerary_details fetches full schedule and blocks IDOR."""
    # Owner access
    details = get_itinerary_details(db=db_session, user_id=1, trip_id=user_trip.id)
    assert details["trip_id"] == user_trip.id
    assert "days" in details
    assert len(details["days"]) == 2
    assert details["days"][0]["items"][0]["title"] == "Stay at Luxury Fort Resort"

    # IDOR check: unauthorized user 2
    forbidden = get_itinerary_details(db=db_session, user_id=2, trip_id=user_trip.id)
    assert "error" in forbidden
    assert "Access denied" in forbidden["error"]


def test_tool_propose_itinerary_modification_simulation_no_db_commit(
    db_session: Session, user_trip: Trip, tool_destination: Destination
):
    """
    Verify propose_itinerary_modification accurately simulates cost savings
    and does NOT modify the database records.
    """
    cheaper_hotel = [h for h in tool_destination.hotels if h.name == "Budget Heritage Stay"][0]
    first_item = user_trip.itineraries[0].days[0].items[0]
    original_item_cost = first_item.estimated_cost
    original_trip_total = user_trip.estimated_total

    # Propose swap to cheaper hotel
    proposal = propose_itinerary_modification(
        db=db_session,
        user_id=1,
        trip_id=user_trip.id,
        action="swap",
        item_id=first_item.id,
        replacement_type="hotel",
        replacement_id=cheaper_hotel.id,
    )

    # 1. Proposal structure verification
    assert "proposal_id" in proposal
    assert proposal["action"] == "swap"
    assert proposal["requires_user_confirmation"] is True
    assert proposal["proposed_item"]["title"] == f"Overnight Stay at {cheaper_hotel.name}"

    # 2. Financial calculation check
    # Original hotel: ₹5000, New hotel: ₹2000 -> Savings: ₹3000
    impact = proposal["budget_impact"]
    assert impact["savings"] == 3000.00
    assert impact["cost_delta"] == -3000.00
    assert impact["proposed_estimated_total"] == float(original_trip_total - Decimal("3000.00"))

    # 3. CRITICAL: Database verification that NO commit occurred!
    db_session.expire_all()
    fresh_trip = db_session.get(Trip, user_trip.id)
    fresh_item = db_session.get(ItineraryItem, first_item.id)

    assert fresh_item.title == "Stay at Luxury Fort Resort"
    assert fresh_item.estimated_cost == original_item_cost
    assert fresh_trip.estimated_total == original_trip_total


def test_tool_propose_itinerary_modification_idor(db_session: Session, user_trip: Trip):
    """Verify unauthorized users cannot simulate changes to others' trips."""
    forbidden = propose_itinerary_modification(
        db=db_session,
        user_id=999,
        trip_id=user_trip.id,
        action="swap",
        item_id=1,
    )
    assert "error" in forbidden
    assert "Access denied" in forbidden["error"]


def test_gemini_llm_provider_parses_function_call():
    """Verify GeminiLLMProvider constructs tool payload and parses functionCall candidates."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "functionCall": {
                                "name": "get_travel_history",
                                "args": {},
                            }
                        }
                    ]
                }
            }
        ]
    }

    tools = [
        {
            "name": "get_travel_history",
            "description": "Get past trips",
            "parameters": {"type": "object", "properties": {}},
        }
    ]

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        provider = GeminiLLMProvider(api_key="fake-gemini-key")
        result = provider.generate(
            prompt="Show my trips",
            system_prompt="System",
            tools=tools,
        )

        assert isinstance(result, LLMResponse)
        assert result.has_function_call is True
        assert result.function_call["name"] == "get_travel_history"

        # Check request payload structure
        call_json = mock_post.call_args[1]["json"]
        assert "tools" in call_json
        assert call_json["tools"][0]["function_declarations"][0]["name"] == "get_travel_history"


def test_assistant_chat_autonomous_tool_flow_travel_history(
    client: TestClient, traveller_headers: dict, user_trip: Trip
):
    """End-to-End: Assistant chat triggers get_travel_history and references user trips."""
    response = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={"message": "Can you check all my trips and travel history?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "travel history" in data["reply"].lower() or "trip" in data["reply"].lower()
    assert data["conversation_id"] > 0


def test_assistant_chat_autonomous_tool_flow_proposal(
    client: TestClient, traveller_headers: dict, user_trip: Trip
):
    """End-to-End: Assistant chat proposes an itinerary swap and returns proposed_changes."""
    response = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={
            "message": "Can you swap my hotel to a cheaper hotel to reduce my budget?",
            "trip_id": user_trip.id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["proposed_changes"] is not None
    proposal = data["proposed_changes"]
    assert proposal["action"] == "swap"
    assert proposal["requires_user_confirmation"] is True
    assert "budget_impact" in proposal
    assert proposal["budget_impact"]["proposed_estimated_total"] > 0


def test_execute_proposal_swap_success(
    client: TestClient, traveller_headers: dict, user_trip: Trip, db_session: Session
):
    """Verifies that an authenticated user can safely execute a proposed swap with ACID persistence."""
    # Find the accommodation item to swap and target hotel
    stmt = (
        ItineraryItem.itinerary_day_id.in_(
            [d.id for d in user_trip.itineraries[0].days]
        )
    )
    hotel_item = db_session.query(ItineraryItem).filter(stmt, ItineraryItem.category == "accommodation").first()
    assert hotel_item is not None

    budget_hotel = db_session.query(Hotel).filter(Hotel.destination_id == user_trip.destination_id, Hotel.price_per_night == Decimal("2000.00")).first()
    assert budget_hotel is not None

    payload = {
        "trip_id": user_trip.id,
        "action": "swap",
        "target_item_id": hotel_item.id,
        "replacement_type": "hotel",
        "replacement_id": budget_hotel.id,
        "title": "Budget Heritage Stay",
        "proposal_id": "test-prop-001",
    }

    response = client.post(
        "/api/v1/assistant/execute-proposal",
        headers=traveller_headers,
        json=payload,
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["proposal_id"] == "test-prop-001"
    assert res_data["trip"]["id"] == user_trip.id

    # Verify database state was updated
    db_session.expire_all()
    updated_item = db_session.get(ItineraryItem, hotel_item.id)
    assert updated_item.title == "Budget Heritage Stay"
    assert updated_item.estimated_cost == Decimal("2000.00")


def test_execute_proposal_idor_forbidden(
    client: TestClient, traveller_headers: dict, user_trip: Trip, db_session: Session
):
    """Verifies that executing a proposal against another user's trip returns 403 Forbidden."""
    # Create an unauthorized user and token
    from app.services.auth_service import create_access_token
    unauthorized_user = User(
        email="stranger@example.com",
        password_hash="fakehash",
        full_name="Stranger User",
        role="traveller",
    )
    db_session.add(unauthorized_user)
    db_session.commit()
    db_session.refresh(unauthorized_user)

    token = create_access_token(user_id=unauthorized_user.id, email=unauthorized_user.email, role=unauthorized_user.role)
    unauth_headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "trip_id": user_trip.id,
        "action": "swap",
        "target_item_id": 999,
        "replacement_type": "hotel",
        "replacement_id": 1,
    }

    response = client.post(
        "/api/v1/assistant/execute-proposal",
        headers=unauth_headers,
        json=payload,
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_execute_proposal_not_found(client: TestClient, traveller_headers: dict):
    """Verifies that executing a proposal on a non-existent trip returns 404."""
    payload = {
        "trip_id": 99999,
        "action": "swap",
        "target_item_id": 1,
        "replacement_type": "hotel",
        "replacement_id": 1,
    }
    response = client.post(
        "/api/v1/assistant/execute-proposal",
        headers=traveller_headers,
        json=payload,
    )
    assert response.status_code == 404


def test_propose_itinerary_modification_missing_entity(db_session: Session, user_trip: Trip):
    """Edge Case: propose_itinerary_modification returns structured error for non-existent catalogue item."""
    item = user_trip.itineraries[0].days[0].items[0]
    result = propose_itinerary_modification(
        db=db_session,
        user_id=user_trip.user_id,
        trip_id=user_trip.id,
        action="swap",
        item_id=item.id,
        replacement_type="hotel",
        replacement_id=999999,
    )
    assert "error" in result
    assert "Hotel #999999 does not exist in the catalogue" in result["error"]


def test_execute_proposal_missing_replacement_entity(
    client: TestClient, traveller_headers: dict, user_trip: Trip
):
    """Edge Case: Executing a proposal referencing a non-existent catalogue item returns 404."""
    item = user_trip.itineraries[0].days[0].items[0]
    payload = {
        "trip_id": user_trip.id,
        "action": "swap",
        "target_item_id": item.id,
        "replacement_type": "hotel",
        "replacement_id": 999999,
    }
    response = client.post(
        "/api/v1/assistant/execute-proposal",
        headers=traveller_headers,
        json=payload,
    )
    assert response.status_code == 404
    assert "Hotel #999999 not found" in response.json()["detail"]


def test_execute_proposal_integrity_error_rollback(
    client: TestClient, traveller_headers: dict, user_trip: Trip
):
    """Edge Case: IntegrityError during commit triggers rollback and returns 400 with user-friendly message."""
    from sqlalchemy.exc import IntegrityError
    from app.services.trip_service import TripService

    item = user_trip.itineraries[0].days[0].items[0]
    payload = {
        "trip_id": user_trip.id,
        "action": "swap",
        "target_item_id": item.id,
        "replacement_type": "hotel",
        "replacement_id": 1,
    }

    mock_integrity = IntegrityError(
        statement="UPDATE trips SET estimated_total = -500",
        params={},
        orig=Exception("check_trip_est_total constraint failed"),
    )

    with patch.object(TripService, "swap_itinerary_item", side_effect=mock_integrity):
        response = client.post(
            "/api/v1/assistant/execute-proposal",
            headers=traveller_headers,
            json=payload,
        )
        assert response.status_code == 400
        assert "violates trip budget constraints" in response.json()["detail"]


def test_propose_itinerary_modification_clear_day(db_session: Session, user_trip: Trip):
    """Verify propose_itinerary_modification simulates clearing an entire day's schedule."""
    res = propose_itinerary_modification(
        db=db_session,
        user_id=user_trip.user_id,
        trip_id=user_trip.id,
        action="clear_day",
        day_number=1,
    )
    assert "error" not in res
    assert res["action"] == "clear_day"
    assert res["target_day_number"] == 1
    assert "cancellation" in res["summary"].lower()
    assert res["budget_impact"]["savings"] > 0
    assert res["requires_user_confirmation"] is True


def test_execute_proposal_clear_day(client: TestClient, traveller_headers: dict, user_trip: Trip):
    """Verify executing a clear_day proposal deletes all items on that day and recalculates totals."""
    payload = {
        "trip_id": user_trip.id,
        "action": "clear_day",
        "day_number": 1,
    }
    response = client.post(
        "/api/v1/assistant/execute-proposal",
        headers=traveller_headers,
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Verify Day 1 has 0 items
    day1 = [d for d in data["trip"]["itineraries"][0]["days"] if d["day_number"] == 1][0]
    assert len(day1["items"]) == 0


def test_assistant_chat_cancel_plans_for_day(client: TestClient, traveller_headers: dict, user_trip: Trip):
    """Verify 'cancel all the plans for day 1' triggers day proposal/clarification, NOT generic pacing advice."""
    response = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={
            "message": "I want to cancel all the plans for day 1",
            "trip_id": user_trip.id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    # Must NOT return generic itinerary pacing advice
    assert "balance high-energy morning sightseeing" not in data["reply"].lower()
    # Should contain proposed_changes or clarification_request
    assert data["proposed_changes"] is not None or data["clarification_request"] is not None

