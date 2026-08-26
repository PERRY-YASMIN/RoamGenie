from datetime import date, timedelta
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.catalogue import Attraction, Destination, Hotel, Restaurant, TransportOption
from app.db.models.finance import BudgetAllocation, SavedTrip
from app.db.models.trip import Itinerary, ItineraryDay, ItineraryItem, PackingItem, Trip, TripMember


@pytest.fixture
def seed_destination(db_session: Session) -> Destination:
    """Create a sample destination with full catalogue."""
    dest = Destination(
        city="Jaipur",
        country="India",
        description="The Pink City of Rajasthan",
        average_daily_cost=Decimal("4000.00"),
        active=True,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)

    hotel1 = Hotel(destination_id=dest.id, name="Royal Palace Heritage", price_per_night=Decimal("3500.00"), rating=Decimal("4.8"))
    hotel2 = Hotel(destination_id=dest.id, name="Budget Inn Jaipur", price_per_night=Decimal("1200.00"), rating=Decimal("4.0"))
    
    rest1 = Restaurant(destination_id=dest.id, name="LMB Sweets & Dining", cuisine="Rajasthani Thali", average_cost_per_person=Decimal("300.00"), rating=Decimal("4.7"))
    rest2 = Restaurant(destination_id=dest.id, name="Peacock Rooftop", cuisine="North Indian", average_cost_per_person=Decimal("500.00"), rating=Decimal("4.5"))
    
    att1 = Attraction(destination_id=dest.id, name="Amber Fort", category="heritage", entry_fee=Decimal("100.00"), rating=Decimal("4.9"))
    att2 = Attraction(destination_id=dest.id, name="Hawa Mahal", category="heritage", entry_fee=Decimal("50.00"), rating=Decimal("4.7"))
    att3 = Attraction(destination_id=dest.id, name="City Palace", category="heritage", entry_fee=Decimal("200.00"), rating=Decimal("4.6"))
    
    trans1 = TransportOption(origin="Delhi", destination_id=dest.id, mode="train", provider="Ajmer Shatabdi", estimated_cost=Decimal("650.00"), duration_minutes=270)
    trans2 = TransportOption(origin="Delhi", destination_id=dest.id, mode="flight", provider="IndiGo", estimated_cost=Decimal("2500.00"), duration_minutes=55)

    db_session.add_all([hotel1, hotel2, rest1, rest2, att1, att2, att3, trans1, trans2])
    db_session.commit()
    return dest


def test_create_trip_draft(client: TestClient, traveller_headers: dict, seed_destination: Destination):
    """Test creating a basic trip without immediate plan generation."""
    payload = {
        "destination_id": seed_destination.id,
        "starting_location": "Delhi",
        "start_date": str(date.today() + timedelta(days=10)),
        "end_date": str(date.today() + timedelta(days=12)),
        "traveller_count": 2,
        "total_budget": "20000.00",
        "preferences": ["heritage", "culture"],
        "members": [
            {"display_name": "Arun Kumar", "age_group": "adult"},
            {"display_name": "Priya Kumar", "age_group": "adult"},
        ],
        "generate_plan": False,
    }
    response = client.post("/api/v1/trips", json=payload, headers=traveller_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["destination_city"] == "Jaipur"
    assert data["starting_location"] == "Delhi"
    assert data["status"] == "draft"
    assert len(data["members"]) == 2
    assert len(data["packing_items"]) > 0
    assert data["is_saved"] is False


def test_create_trip_with_auto_plan(client: TestClient, traveller_headers: dict, seed_destination: Destination):
    """Test creating a trip and generating its plan in one request."""
    payload = {
        "destination_id": seed_destination.id,
        "starting_location": "Delhi",
        "start_date": str(date.today() + timedelta(days=10)),
        "end_date": str(date.today() + timedelta(days=12)),
        "traveller_count": 2,
        "total_budget": "20000.00",
        "preferences": ["heritage"],
        "generate_plan": True,
    }
    response = client.post("/api/v1/trips", json=payload, headers=traveller_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "planned"
    assert float(data["estimated_total"]) > 0
    assert len(data["itineraries"]) == 1
    assert len(data["itineraries"][0]["days"]) == 3
    assert len(data["budget_allocations"]) > 0


def test_get_and_list_trips(client: TestClient, traveller_headers: dict, seed_destination: Destination):
    """Test listing user trips and retrieving a single trip by ID."""
    # Create two trips
    for i in range(2):
        client.post(
            "/api/v1/trips",
            json={
                "destination_id": seed_destination.id,
                "starting_location": "Delhi",
                "start_date": str(date.today() + timedelta(days=10 + i * 5)),
                "end_date": str(date.today() + timedelta(days=12 + i * 5)),
                "traveller_count": 1,
                "total_budget": "10000.00",
            },
            headers=traveller_headers,
        )

    # List trips
    list_resp = client.get("/api/v1/trips", headers=traveller_headers)
    assert list_resp.status_code == 200
    trips = list_resp.json()
    assert len(trips) >= 2

    # Get single trip
    first_id = trips[0]["id"]
    get_resp = client.get(f"/api/v1/trips/{first_id}", headers=traveller_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == first_id


def test_update_trip(client: TestClient, traveller_headers: dict, seed_destination: Destination):
    """Test PATCH /api/v1/trips/{id} for partial updates."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 1,
            "total_budget": "15000.00",
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    patch_resp = client.patch(
        f"/api/v1/trips/{trip_id}",
        json={"total_budget": "18000.00", "traveller_count": 3, "starting_location": "Noida"},
        headers=traveller_headers,
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert float(updated["total_budget"]) == 18000.00
    assert updated["traveller_count"] == 3
    assert updated["starting_location"] == "Noida"


def test_delete_trip_cascades(client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session):
    """Test DELETE /api/v1/trips/{id} safely deletes all cascade children."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 2,
            "total_budget": "20000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/v1/trips/{trip_id}", headers=traveller_headers)
    assert del_resp.status_code == 204

    # Verify deleted in database
    assert db_session.get(Trip, trip_id) is None
    # Verify no orphan itineraries
    assert db_session.query(Itinerary).filter(Itinerary.trip_id == trip_id).first() is None


def test_generate_plan_endpoint(client: TestClient, traveller_headers: dict, seed_destination: Destination):
    """Test generating a plan for an existing draft trip."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=13)),
            "traveller_count": 2,
            "total_budget": "25000.00",
            "generate_plan": False,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    gen_resp = client.post(f"/api/v1/trips/{trip_id}/generate", headers=traveller_headers)
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()
    assert gen_data["itinerary"]["trip_id"] == trip_id
    assert len(gen_data["itinerary"]["days"]) == 4
    assert gen_data["budget_summary"]["status"] in ("within_budget", "exact", "over_budget")

    # Verify itinerary get endpoint
    itin_resp = client.get(f"/api/v1/trips/{trip_id}/itinerary", headers=traveller_headers)
    assert itin_resp.status_code == 200
    assert itin_resp.json()["version"] == 1


def test_bookmark_saved_trip(client: TestClient, traveller_headers: dict, seed_destination: Destination):
    """Test saving (bookmarking) and unsaving trips."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 1,
            "total_budget": "10000.00",
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # Bookmark
    save_resp = client.post(f"/api/v1/trips/{trip_id}/save", headers=traveller_headers)
    assert save_resp.status_code == 200
    assert save_resp.json()["is_saved"] is True

    # List saved
    saved_list = client.get("/api/v1/trips/saved", headers=traveller_headers)
    assert saved_list.status_code == 200
    assert any(s["trip_id"] == trip_id for s in saved_list.json())

    # Unsave
    unsave_resp = client.post(f"/api/v1/trips/{trip_id}/save", headers=traveller_headers)
    assert unsave_resp.status_code == 200
    assert unsave_resp.json()["is_saved"] is False


def test_bookmark_nonexistent_trip_returns_404(client: TestClient, traveller_headers: dict):
    """Ensure saving a non-existent trip returns 404 Not Found cleanly."""
    response = client.post("/api/v1/trips/99999/save", headers=traveller_headers)
    assert response.status_code == 404


def test_idor_cross_user_protection(client: TestClient, traveller_headers: dict, seed_destination: Destination):
    """Ensure User A cannot view, edit, generate plans for, bookmark, or delete User B's trip."""
    # Create trip under user A
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 1,
            "total_budget": "10000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # Register and login User B
    client.post(
        "/api/v1/auth/register",
        json={"email": "user_b@example.com", "password": "UserBPassword123!", "full_name": "User B"},
    )
    login_b = client.post(
        "/api/v1/auth/login",
        json={"email": "user_b@example.com", "password": "UserBPassword123!"},
    )
    user_b_headers = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    # User B attempts to access User A's trip across every endpoint
    assert client.get(f"/api/v1/trips/{trip_id}", headers=user_b_headers).status_code in (403, 404)
    assert client.patch(f"/api/v1/trips/{trip_id}", json={"total_budget": "99999.00"}, headers=user_b_headers).status_code in (403, 404)
    assert client.post(f"/api/v1/trips/{trip_id}/generate", headers=user_b_headers).status_code in (403, 404)
    assert client.post(f"/api/v1/trips/{trip_id}/ai-plan", headers=user_b_headers).status_code in (403, 404)
    assert client.post(f"/api/v1/trips/{trip_id}/plan", headers=user_b_headers).status_code in (403, 404)
    assert client.get(f"/api/v1/trips/{trip_id}/itinerary", headers=user_b_headers).status_code in (403, 404)
    assert client.get(f"/api/v1/trips/{trip_id}/weather", headers=user_b_headers).status_code in (403, 404)
    assert client.post(f"/api/v1/trips/{trip_id}/save", headers=user_b_headers).status_code in (403, 404)
    assert client.delete(f"/api/v1/trips/{trip_id}", headers=user_b_headers).status_code in (403, 404)


def test_child_packing_item_idor_protection(client: TestClient, traveller_headers: dict, seed_destination: Destination):
    """Ensure User B cannot list, add, toggle, or delete packing items on User A's trip."""
    # User A creates trip
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 1,
            "total_budget": "10000.00",
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]
    packing_items = create_resp.json()["packing_items"]
    item_id = packing_items[0]["id"]

    # Register and login User B
    client.post(
        "/api/v1/auth/register",
        json={"email": "user_c@example.com", "password": "UserCPassword123!", "full_name": "User C"},
    )
    login_c = client.post(
        "/api/v1/auth/login",
        json={"email": "user_c@example.com", "password": "UserCPassword123!"},
    )
    user_c_headers = {"Authorization": f"Bearer {login_c.json()['access_token']}"}

    # User C attempts to access User A's packing items
    assert client.get(f"/api/v1/assistant/trips/{trip_id}/packing", headers=user_c_headers).status_code == 404
    assert client.post(f"/api/v1/assistant/trips/{trip_id}/packing", json={"item": "Hacked Item", "category": "General"}, headers=user_c_headers).status_code == 404
    assert client.patch(f"/api/v1/assistant/packing/{item_id}", json={"is_packed": True}, headers=user_c_headers).status_code == 403
    assert client.delete(f"/api/v1/assistant/packing/{item_id}", headers=user_c_headers).status_code == 403


def test_assistant_chat_context_isolation(client: TestClient, traveller_headers: dict, seed_destination: Destination):
    """Ensure User B passing User A's trip_id in AI chat does not leak User A's destination/budget context."""
    # User A creates expensive trip
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 4,
            "total_budget": "99999.00",
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # Register and login User D
    client.post(
        "/api/v1/auth/register",
        json={"email": "user_d@example.com", "password": "UserDPassword123!", "full_name": "User D"},
    )
    login_d = client.post(
        "/api/v1/auth/login",
        json={"email": "user_d@example.com", "password": "UserDPassword123!"},
    )
    user_d_headers = {"Authorization": f"Bearer {login_d.json()['access_token']}"}

    # User D sends chat message passing User A's trip_id -> should be rejected with 403 Forbidden
    chat_resp = client.post(
        "/api/v1/assistant/chat",
        json={"message": "What should I pack?", "trip_id": trip_id},
        headers=user_d_headers,
    )
    assert chat_resp.status_code == 403
    assert "Access denied" in chat_resp.json()["detail"]


def test_admin_access_allowed(client: TestClient, traveller_headers: dict, admin_headers: dict, seed_destination: Destination):
    """Ensure system administrators can view and manage trips across accounts."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 1,
            "total_budget": "10000.00",
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # Admin accesses the trip
    get_resp = client.get(f"/api/v1/trips/{trip_id}", headers=admin_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == trip_id


def test_trip_deletion_cascades_all_relational_tables(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """Verify that deleting a trip cascades and deletes all related rows in relational tables."""
    # Create trip with full plan, members, packing items
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=13)),
            "traveller_count": 2,
            "total_budget": "30000.00",
            "members": [{"display_name": "Test Member", "age_group": "adult"}],
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # Bookmark trip
    client.post(f"/api/v1/trips/{trip_id}/save", headers=traveller_headers)

    # Verify rows exist before deletion
    assert db_session.query(Itinerary).filter(Itinerary.trip_id == trip_id).count() >= 1
    assert db_session.query(BudgetAllocation).filter(BudgetAllocation.trip_id == trip_id).count() >= 1
    assert db_session.query(PackingItem).filter(PackingItem.trip_id == trip_id).count() >= 1
    assert db_session.query(SavedTrip).filter(SavedTrip.trip_id == trip_id).count() == 1
    assert db_session.query(TripMember).filter(TripMember.trip_id == trip_id).count() >= 1

    # Delete trip
    del_resp = client.delete(f"/api/v1/trips/{trip_id}", headers=traveller_headers)
    assert del_resp.status_code == 204

    # Verify all cascade children are deleted
    assert db_session.get(Trip, trip_id) is None
    assert db_session.query(Itinerary).filter(Itinerary.trip_id == trip_id).count() == 0
    assert db_session.query(BudgetAllocation).filter(BudgetAllocation.trip_id == trip_id).count() == 0
    assert db_session.query(PackingItem).filter(PackingItem.trip_id == trip_id).count() == 0
    assert db_session.query(SavedTrip).filter(SavedTrip.trip_id == trip_id).count() == 0
    assert db_session.query(TripMember).filter(TripMember.trip_id == trip_id).count() == 0


def test_saved_trip_reload_structure(
    client: TestClient, traveller_headers: dict, seed_destination: Destination
):
    """Verify that GET /api/v1/trips/{id} returns a completely hydrated structure for PlanPage."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 2,
            "total_budget": "20000.00",
            "preferences": ["heritage"],
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # Bookmark trip
    client.post(f"/api/v1/trips/{trip_id}/save", headers=traveller_headers)

    # Fetch trip for reload
    get_resp = client.get(f"/api/v1/trips/{trip_id}", headers=traveller_headers)
    assert get_resp.status_code == 200
    data = get_resp.json()

    # Assert all required hydration properties are present
    assert data["id"] == trip_id
    assert data["destination_id"] == seed_destination.id
    assert data["destination_city"] == "Jaipur"
    assert data["starting_location"] == "Delhi"
    assert data["start_date"] == str(date.today() + timedelta(days=10))
    assert data["end_date"] == str(date.today() + timedelta(days=12))
    assert data["traveller_count"] == 2
    assert float(data["total_budget"]) == 20000.00
    assert data["is_saved"] is True

    # Assert itineraries with days and items
    assert len(data["itineraries"]) >= 1
    first_itin = data["itineraries"][0]
    assert len(first_itin["days"]) == 3
    for day in first_itin["days"]:
        assert len(day["items"]) > 0
        for item in day["items"]:
            assert item["title"]
            assert item["category"]
            assert float(item["estimated_cost"]) >= 0

    # Assert budget allocations & summary
    assert data["budget_summary"] is not None
    assert len(data["budget_summary"]["categories"]) > 0

    # Assert packing checklist items
    assert len(data["packing_items"]) > 0


def test_saved_trip_reload_does_not_duplicate_or_mutate_database(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """CRITICAL: Verify that reloading a saved trip never regenerates or duplicates database rows."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 2,
            "total_budget": "20000.00",
            "preferences": ["heritage"],
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # Capture initial entity IDs and row counts
    itin_count_before = db_session.query(Itinerary).filter(Itinerary.trip_id == trip_id).count()
    days_count_before = db_session.query(ItineraryDay).count()
    items_count_before = db_session.query(ItineraryItem).count()
    alloc_count_before = db_session.query(BudgetAllocation).filter(BudgetAllocation.trip_id == trip_id).count()
    pack_count_before = db_session.query(PackingItem).filter(PackingItem.trip_id == trip_id).count()

    initial_itin = db_session.query(Itinerary).filter(Itinerary.trip_id == trip_id).first()
    initial_itin_id = initial_itin.id
    initial_itin_version = initial_itin.version

    # Simulate opening/reloading the saved trip 5 times
    for _ in range(5):
        resp = client.get(f"/api/v1/trips/{trip_id}", headers=traveller_headers)
        assert resp.status_code == 200

    # Assert strict non-duplication
    assert db_session.query(Itinerary).filter(Itinerary.trip_id == trip_id).count() == itin_count_before
    assert db_session.query(ItineraryDay).count() == days_count_before
    assert db_session.query(ItineraryItem).count() == items_count_before
    assert db_session.query(BudgetAllocation).filter(BudgetAllocation.trip_id == trip_id).count() == alloc_count_before
    assert db_session.query(PackingItem).filter(PackingItem.trip_id == trip_id).count() == pack_count_before

    current_itin = db_session.query(Itinerary).filter(Itinerary.trip_id == trip_id).first()
    assert current_itin.id == initial_itin_id
    assert current_itin.version == initial_itin_version


def test_swap_itinerary_item_hotel_success(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """M4: Test successfully swapping an accommodation item with a catalogue hotel and recalculating budget."""
    # 1. Create trip and auto-plan
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 2,
            "total_budget": "20000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # 2. Add alternative hotel in same destination
    alt_hotel = Hotel(
        destination_id=seed_destination.id,
        name="Luxury Palace Resort",
        price_per_night=Decimal("8000.00"),
        rating=Decimal("4.9"),
    )
    db_session.add(alt_hotel)
    db_session.commit()
    db_session.refresh(alt_hotel)

    # 3. Find accommodation item
    trip_data = client.get(f"/api/v1/trips/{trip_id}", headers=traveller_headers).json()
    hotel_item = None
    for day in trip_data["itineraries"][0]["days"]:
        for itm in day["items"]:
            if itm["category"] == "accommodation":
                hotel_item = itm
                break
        if hotel_item:
            break
    assert hotel_item is not None

    # 4. Swap item with alt_hotel
    swap_resp = client.patch(
        f"/api/v1/trips/{trip_id}/itinerary/items/{hotel_item['id']}",
        json={
            "replacement_type": "hotel",
            "replacement_id": alt_hotel.id,
        },
        headers=traveller_headers,
    )
    assert swap_resp.status_code == 200
    updated = swap_resp.json()

    # 5. Verify updated item and budget recalculation
    updated_item = None
    for day in updated["itineraries"][0]["days"]:
        for itm in day["items"]:
            if itm["id"] == hotel_item["id"]:
                updated_item = itm
                break
    assert updated_item is not None
    assert "Luxury Palace Resort" in updated_item["title"]
    assert float(updated_item["estimated_cost"]) == 8000.00

    # Verify accommodation category allocation reflects 8000.00
    accom_alloc = next(
        (c for c in updated["budget_summary"]["categories"] if c["category"] == "accommodation"),
        None,
    )
    assert accom_alloc is not None
    assert float(accom_alloc["amount"]) >= 8000.00


def test_swap_itinerary_item_dining_and_attraction_success(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """M4: Test swapping dining and attraction events with per-traveller cost recalculation."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 3,
            "total_budget": "30000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    # Add alt restaurant and attraction
    alt_rest = Restaurant(
        destination_id=seed_destination.id,
        name="Royal Dining Hall",
        cuisine="Rajasthani",
        average_cost_per_person=Decimal("500.00"),
        rating=Decimal("4.8"),
    )
    alt_att = Attraction(
        destination_id=seed_destination.id,
        name="Jaigarh Fort",
        category="heritage",
        entry_fee=Decimal("200.00"),
        rating=Decimal("4.6"),
    )
    db_session.add_all([alt_rest, alt_att])
    db_session.commit()

    trip_data = client.get(f"/api/v1/trips/{trip_id}", headers=traveller_headers).json()
    food_item = None
    att_item = None
    for day in trip_data["itineraries"][0]["days"]:
        for itm in day["items"]:
            if itm["category"] == "food" and not food_item:
                food_item = itm
            elif itm["category"] in ("attraction", "attractions") and not att_item:
                att_item = itm

    assert food_item is not None
    assert att_item is not None

    # Swap food item (500 * 3 travellers = 1500)
    swap_food = client.patch(
        f"/api/v1/trips/{trip_id}/itinerary/items/{food_item['id']}",
        json={"replacement_type": "restaurant", "replacement_id": alt_rest.id},
        headers=traveller_headers,
    )
    assert swap_food.status_code == 200
    updated_trip = swap_food.json()
    new_food = next(
        itm
        for day in updated_trip["itineraries"][0]["days"]
        for itm in day["items"]
        if itm["id"] == food_item["id"]
    )
    assert "Royal Dining Hall" in new_food["title"]
    assert float(new_food["estimated_cost"]) == 1500.00

    # Swap attraction item (200 * 3 travellers = 600)
    swap_att = client.patch(
        f"/api/v1/trips/{trip_id}/itinerary/items/{att_item['id']}",
        json={"replacement_type": "attraction", "replacement_id": alt_att.id},
        headers=traveller_headers,
    )
    assert swap_att.status_code == 200
    updated_trip2 = swap_att.json()
    new_att = next(
        itm
        for day in updated_trip2["itineraries"][0]["days"]
        for itm in day["items"]
        if itm["id"] == att_item["id"]
    )
    assert "Jaigarh Fort" in new_att["title"]
    assert float(new_att["estimated_cost"]) == 600.00


def test_swap_itinerary_item_idor_rejected(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """M4: Ensure User B cannot modify User A's itinerary items (IDOR protection)."""
    # Create trip under User A
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 1,
            "total_budget": "10000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]
    item_id = create_resp.json()["itineraries"][0]["days"][0]["items"][0]["id"]

    # Register and login User B
    client.post(
        "/api/v1/auth/register",
        json={"email": "attacker_m4@example.com", "password": "SecurePassword123!", "full_name": "Attacker M4"},
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "attacker_m4@example.com", "password": "SecurePassword123!"},
    )
    attacker_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # User B attempts to swap User A's itinerary item
    swap_resp = client.patch(
        f"/api/v1/trips/{trip_id}/itinerary/items/{item_id}",
        json={"replacement_type": "attraction", "replacement_id": 1},
        headers=attacker_headers,
    )
    assert swap_resp.status_code in (403, 404)


def test_swap_itinerary_item_cross_destination_rejected(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """M4: Ensure swapping with a catalogue entity from an unrelated destination is rejected."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 1,
            "total_budget": "10000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]
    item_id = create_resp.json()["itineraries"][0]["days"][0]["items"][0]["id"]

    # Create unrelated destination and hotel
    other_dest = Destination(city="Kochi", country="India", active=True)
    db_session.add(other_dest)
    db_session.commit()
    other_hotel = Hotel(destination_id=other_dest.id, name="Kochi Backwaters Inn", price_per_night=Decimal("3000.00"))
    db_session.add(other_hotel)
    db_session.commit()

    # Attempt cross-destination swap
    swap_resp = client.patch(
        f"/api/v1/trips/{trip_id}/itinerary/items/{item_id}",
        json={"replacement_type": "hotel", "replacement_id": other_hotel.id},
        headers=traveller_headers,
    )
    assert swap_resp.status_code == 400
    assert "does not belong to trip destination" in swap_resp.json()["detail"]


def test_swap_itinerary_item_incompatible_category_rejected(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """M4: Ensure swapping an item with an incompatible catalogue category is rejected."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 1,
            "total_budget": "10000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]
    trip_data = create_resp.json()

    # Find attraction item
    att_item = next(
        itm
        for day in trip_data["itineraries"][0]["days"]
        for itm in day["items"]
        if itm["category"] in ("attraction", "attractions")
    )

    hotel = db_session.query(Hotel).filter(Hotel.destination_id == seed_destination.id).first()

    # Attempt to replace attraction with hotel
    swap_resp = client.patch(
        f"/api/v1/trips/{trip_id}/itinerary/items/{att_item['id']}",
        json={"replacement_type": "hotel", "replacement_id": hotel.id},
        headers=traveller_headers,
    )
    assert swap_resp.status_code == 400
    assert "Cannot replace" in swap_resp.json()["detail"]



def test_swap_itinerary_item_persists_on_reload(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """M4: Ensure item replacement and recalculated budget persist across page reloads."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 2,
            "total_budget": "20000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    alt_hotel = Hotel(
        destination_id=seed_destination.id,
        name="Heritage Haveli Deluxe",
        price_per_night=Decimal("4500.00"),
        rating=Decimal("4.7"),
    )
    db_session.add(alt_hotel)
    db_session.commit()

    hotel_item = next(
        itm
        for day in create_resp.json()["itineraries"][0]["days"]
        for itm in day["items"]
        if itm["category"] == "accommodation"
    )

    # Perform swap
    client.patch(
        f"/api/v1/trips/{trip_id}/itinerary/items/{hotel_item['id']}",
        json={"replacement_type": "hotel", "replacement_id": alt_hotel.id},
        headers=traveller_headers,
    )

    # Reload trip via GET /trips/{id}
    reloaded = client.get(f"/api/v1/trips/{trip_id}", headers=traveller_headers).json()
    reloaded_item = next(
        itm
        for day in reloaded["itineraries"][0]["days"]
        for itm in day["items"]
        if itm["id"] == hotel_item["id"]
    )
    assert "Heritage Haveli Deluxe" in reloaded_item["title"]
    assert float(reloaded_item["estimated_cost"]) == 4500.00


def test_swap_itinerary_item_transport_success(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """M4: Test swapping transit options and verifying per-traveller transportation allocation."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 2,
            "total_budget": "20000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]

    alt_flight = TransportOption(
        origin="Delhi",
        destination_id=seed_destination.id,
        mode="flight",
        provider="Air India Express",
        estimated_cost=Decimal("3200.00"),
        duration_minutes=60,
    )
    db_session.add(alt_flight)
    db_session.commit()

    trans_item = next(
        itm
        for day in create_resp.json()["itineraries"][0]["days"]
        for itm in day["items"]
        if itm["category"] == "transportation"
    )

    # Swap transit option (3200 * 2 travellers = 6400)
    swap_resp = client.patch(
        f"/api/v1/trips/{trip_id}/itinerary/items/{trans_item['id']}",
        json={"replacement_type": "transport", "replacement_id": alt_flight.id},
        headers=traveller_headers,
    )
    assert swap_resp.status_code == 200
    updated = swap_resp.json()

    updated_trans = next(
        itm
        for day in updated["itineraries"][0]["days"]
        for itm in day["items"]
        if itm["id"] == trans_item["id"]
    )
    assert "Air India Express" in updated_trans["notes"]
    assert float(updated_trans["estimated_cost"]) == 6400.00


def test_swap_itinerary_item_transaction_rollback_on_failure(
    client: TestClient, traveller_headers: dict, seed_destination: Destination, db_session: Session
):
    """M4: Verify that if swap fails due to non-existent replacement entity, the database rolls back cleanly."""
    create_resp = client.post(
        "/api/v1/trips",
        json={
            "destination_id": seed_destination.id,
            "starting_location": "Delhi",
            "start_date": str(date.today() + timedelta(days=10)),
            "end_date": str(date.today() + timedelta(days=12)),
            "traveller_count": 1,
            "total_budget": "15000.00",
            "generate_plan": True,
        },
        headers=traveller_headers,
    )
    trip_id = create_resp.json()["id"]
    original_item = create_resp.json()["itineraries"][0]["days"][0]["items"][0]
    original_title = original_item["title"]
    original_cost = original_item["estimated_cost"]

    # Attempt swap with non-existent catalogue ID 999999
    fail_resp = client.patch(
        f"/api/v1/trips/{trip_id}/itinerary/items/{original_item['id']}",
        json={"replacement_type": "hotel", "replacement_id": 999999},
        headers=traveller_headers,
    )
    assert fail_resp.status_code == 404

    # Assert original item in database is completely untouched
    db_item = db_session.get(ItineraryItem, original_item["id"])
    assert db_item.title == original_title
    assert str(db_item.estimated_cost) == str(original_cost)



