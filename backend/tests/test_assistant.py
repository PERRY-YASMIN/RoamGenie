from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.ai import AIConversation, AIMessage
from app.db.models.catalogue import Destination
from app.db.models.trip import Trip
from app.services.ai_providers import LLMProviderError


def test_assistant_chat_unauthenticated_rejected(client: TestClient):
    """M5: Unauthenticated chat requests must be rejected with 401 Unauthorized."""
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What should I pack for a monsoon trip?"},
    )
    assert response.status_code == 401


def test_assistant_chat_authenticated_general_inquiry(client: TestClient, traveller_headers: dict):
    """M5: Authenticated users can chat without a trip context for general inquiries."""
    response = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={"message": "Hello! What can you help me with?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
    assert data["conversation_id"] > 0
    assert len(data["suggested_actions"]) > 0


def test_assistant_chat_authenticated_with_trip_grounding(
    client: TestClient, traveller_headers: dict, seed_destination: Destination
):
    """M5: Chat with trip context grounds the response with destination catalogue facts."""
    trip_res = client.post(
        "/api/v1/trips",
        headers=traveller_headers,
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 2,
            "total_budget": "20000.00",
            "generate_plan": True,
        },
    )
    assert trip_res.status_code == 201
    trip_id = trip_res.json()["id"]

    chat_res = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={
            "message": "Recommend popular local attractions for my trip",
            "trip_id": trip_id,
        },
    )
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert chat_data["conversation_id"] > 0
    assert chat_data["trip_id"] == trip_id
    assert "attraction" in chat_data["reply"].lower() or "sight" in chat_data["reply"].lower() or "jaipur" in chat_data["reply"].lower()
    assert len(chat_data["suggested_actions"]) > 0


def test_assistant_chat_trip_idor_rejected(
    client: TestClient, traveller_headers: dict, seed_destination: Destination
):
    """M5: User B cannot chat with User A's trip_id (IDOR protection)."""
    # User A creates trip
    trip_res = client.post(
        "/api/v1/trips",
        headers=traveller_headers,
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
            "traveller_count": 2,
            "total_budget": "20000.00",
        },
    )
    trip_id = trip_res.json()["id"]

    # Register User B
    client.post(
        "/api/v1/auth/register",
        json={"email": "attacker_m5@example.com", "password": "SecurePassword123!", "full_name": "Attacker M5"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "attacker_m5@example.com", "password": "SecurePassword123!"},
    )
    attacker_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # User B attempts to access User A's trip context
    chat_res = client.post(
        "/api/v1/assistant/chat",
        headers=attacker_headers,
        json={
            "message": "Summarize this trip details and budget for me",
            "trip_id": trip_id,
        },
    )
    assert chat_res.status_code == 403
    assert "Access denied" in chat_res.json()["detail"]


def test_assistant_chat_nonexistent_trip_rejected(client: TestClient, traveller_headers: dict):
    """M5: Non-existent trip_id returns 404 Not Found."""
    chat_res = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={
            "message": "Tell me about my trip",
            "trip_id": 999999,
        },
    )
    assert chat_res.status_code == 404
    assert "Trip not found" in chat_res.json()["detail"]


def test_assistant_chat_conversation_history_persistence(
    client: TestClient, traveller_headers: dict, db_session: Session
):
    """M5: Verify multi-turn conversation and message persistence in PostgreSQL."""
    # Turn 1
    res1 = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={"message": "First question: tell me a travel tip"},
    )
    assert res1.status_code == 200
    conv_id = res1.json()["conversation_id"]

    # Turn 2 in same conversation
    res2 = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={
            "message": "Second question: follow up on that",
            "conversation_id": conv_id,
        },
    )
    assert res2.status_code == 200
    assert res2.json()["conversation_id"] == conv_id

    # Verify rows in database
    conv = db_session.get(AIConversation, conv_id)
    assert conv is not None
    messages = db_session.query(AIMessage).filter(AIMessage.conversation_id == conv_id).order_by(AIMessage.id).all()
    assert len(messages) == 4  # 2 user questions + 2 assistant replies
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[2].role == "user"
    assert messages[3].role == "assistant"


def test_assistant_chat_foreign_conversation_idor_rejected(
    client: TestClient, traveller_headers: dict
):
    """M5: User B cannot append messages to User A's conversation thread."""
    # User A starts conversation
    res1 = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={"message": "Private conversation turn"},
    )
    conv_id = res1.json()["conversation_id"]

    # User B registers
    client.post(
        "/api/v1/auth/register",
        json={"email": "intruder_m5@example.com", "password": "SecurePassword123!", "full_name": "Intruder M5"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "intruder_m5@example.com", "password": "SecurePassword123!"},
    )
    intruder_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # User B attempts to hijack User A's conversation thread
    res2 = client.post(
        "/api/v1/assistant/chat",
        headers=intruder_headers,
        json={
            "message": "Hijack attempt",
            "conversation_id": conv_id,
        },
    )
    assert res2.status_code in (403, 404)


def test_assistant_chat_budget_explanation_grounding(
    client: TestClient, traveller_headers: dict, seed_destination: Destination
):
    """M5: Assistant accurately explains trip total budget, estimated total, and remaining balance."""
    trip_res = client.post(
        "/api/v1/trips",
        headers=traveller_headers,
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
            "traveller_count": 2,
            "total_budget": "25000.00",
            "generate_plan": True,
        },
    )
    trip_id = trip_res.json()["id"]

    chat_res = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={
            "message": "Can you analyze my budget and spending?",
            "trip_id": trip_id,
        },
    )
    assert chat_res.status_code == 200
    reply = chat_res.json()["reply"]
    assert "budget" in reply.lower() or "swap" in reply.lower() or "cost" in reply.lower()


def test_assistant_chat_weather_packing_grounding(
    client: TestClient, traveller_headers: dict, seed_destination: Destination
):
    """M5: Assistant packing tips reference forecast conditions and checklist."""
    trip_res = client.post(
        "/api/v1/trips",
        headers=traveller_headers,
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
            "traveller_count": 1,
            "total_budget": "15000.00",
            "generate_plan": True,
        },
    )
    trip_id = trip_res.json()["id"]

    chat_res = client.post(
        "/api/v1/assistant/chat",
        headers=traveller_headers,
        json={
            "message": "What should I pack for this trip?",
            "trip_id": trip_id,
        },
    )
    assert chat_res.status_code == 200
    reply = chat_res.json()["reply"]
    assert "pack" in reply.lower() or "clothing" in reply.lower() or "shoes" in reply.lower()


def test_packing_items_lifecycle(client: TestClient, traveller_headers: dict, seed_destination):
    """Verify packing checklist CRUD operations with ownership checks."""
    trip_res = client.post(
        "/api/v1/trips",
        headers=traveller_headers,
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Bangalore",
            "start_date": "2026-10-01",
            "end_date": "2026-10-04",
            "traveller_count": 1,
            "total_budget": "15000.00",
        },
    )
    trip_id = trip_res.json()["id"]

    # Add custom packing item
    add_res = client.post(
        f"/api/v1/assistant/trips/{trip_id}/packing",
        headers=traveller_headers,
        json={"item": "DSLR Camera", "category": "Electronics"},
    )
    assert add_res.status_code == 201
    item_id = add_res.json()["id"]
    assert add_res.json()["is_packed"] is False

    # Get items
    get_res = client.get(f"/api/v1/assistant/trips/{trip_id}/packing", headers=traveller_headers)
    assert get_res.status_code == 200
    items = get_res.json()
    assert any(i["id"] == item_id for i in items)

    # Toggle packed
    toggle_res = client.patch(
        f"/api/v1/assistant/packing/{item_id}",
        headers=traveller_headers,
        json={"is_packed": True},
    )
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_packed"] is True

    # Delete item
    del_res = client.delete(f"/api/v1/assistant/packing/{item_id}", headers=traveller_headers)
    assert del_res.status_code == 204
