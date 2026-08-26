from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.catalogue import (
    Attraction,
    Destination,
    Hotel,
    Restaurant,
    TransportOption,
)


def seed_catalogue(db: Session) -> Destination:
    """Helper to seed sample catalogue data."""
    dest = Destination(
        city="Mysuru",
        country="India",
        description="Heritage and palaces",
        average_daily_cost=3500.00,
        active=True,
    )
    db.add(dest)
    db.commit()
    db.refresh(dest)

    hotel = Hotel(
        destination_id=dest.id,
        name="Heritage Palace Stay",
        price_per_night=3200.00,
        rating=4.5,
    )
    restaurant = Restaurant(
        destination_id=dest.id,
        name="Royal Tiffin",
        cuisine="South Indian",
        average_cost_per_person=400.00,
        rating=4.6,
    )
    attraction = Attraction(
        destination_id=dest.id,
        name="Mysuru Palace",
        category="heritage",
        entry_fee=100.00,
        rating=4.8,
    )
    transport = TransportOption(
        origin="Chennai",
        destination_id=dest.id,
        mode="train",
        provider="Demo Express",
        estimated_cost=850.00,
        duration_minutes=480,
    )
    db.add_all([hotel, restaurant, attraction, transport])
    db.commit()
    return dest


def test_list_destinations(client: TestClient, db_session: Session) -> None:
    seed_catalogue(db_session)
    response = client.get("/api/v1/destinations")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["city"] == "Mysuru"
    assert items[0]["country"] == "India"


def test_search_destinations(client: TestClient, db_session: Session) -> None:
    seed_catalogue(db_session)
    # Search matching
    resp1 = client.get("/api/v1/destinations?search=mys")
    assert resp1.status_code == 200
    assert len(resp1.json()) == 1

    # Search non-matching
    resp2 = client.get("/api/v1/destinations?search=paris")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 0


def test_get_destination_detail(client: TestClient, db_session: Session) -> None:
    dest = seed_catalogue(db_session)
    response = client.get(f"/api/v1/destinations/{dest.id}")
    assert response.status_code == 200
    assert response.json()["city"] == "Mysuru"


def test_get_destination_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/destinations/99999")
    assert response.status_code == 404


def test_admin_create_destination(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/destinations",
        json={
            "city": "Kochi",
            "country": "India",
            "description": "Coastal history",
            "average_daily_cost": 4000.00,
            "active": True,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    assert response.json()["city"] == "Kochi"


def test_traveller_cannot_create_destination(
    client: TestClient, traveller_headers: dict[str, str]
) -> None:
    response = client.post(
        "/api/v1/destinations",
        json={
            "city": "Goa",
            "country": "India",
            "description": "Beaches",
            "average_daily_cost": 5000.00,
        },
        headers=traveller_headers,
    )
    assert response.status_code == 403


def test_list_hotels_with_filters(client: TestClient, db_session: Session) -> None:
    dest = seed_catalogue(db_session)
    # Filter matching
    resp1 = client.get(f"/api/v1/hotels?destination_id={dest.id}&max_price=4000")
    assert resp1.status_code == 200
    assert len(resp1.json()) == 1

    # Filter out by price
    resp2 = client.get(f"/api/v1/hotels?destination_id={dest.id}&max_price=2000")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 0


def test_list_restaurants_with_filters(
    client: TestClient, db_session: Session
) -> None:
    dest = seed_catalogue(db_session)
    resp1 = client.get(f"/api/v1/restaurants?destination_id={dest.id}&cuisine=south")
    assert resp1.status_code == 200
    assert len(resp1.json()) == 1

    resp2 = client.get(f"/api/v1/restaurants?destination_id={dest.id}&cuisine=italian")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 0


def test_list_attractions_with_filters(
    client: TestClient, db_session: Session
) -> None:
    dest = seed_catalogue(db_session)
    resp = client.get(
        f"/api/v1/attractions?destination_id={dest.id}&category=heritage"
    )
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Mysuru Palace"


def test_list_transport_options(client: TestClient, db_session: Session) -> None:
    seed_catalogue(db_session)
    resp = client.get("/api/v1/transport-options?origin=chennai&mode=train")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["provider"] == "Demo Express"
