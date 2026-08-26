from decimal import Decimal
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models import Base, User
from app.db.models.catalogue import Attraction, Destination, Hotel, Restaurant, TransportOption
from app.db.session import get_db
from app.main import app
from app.services.auth_service import hash_password

# Test database setup (in-memory SQLite shared across single thread)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database schema for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def traveller_token(client: TestClient) -> str:
    """Register and log in a regular traveller, returning JWT access token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "traveller@example.com",
            "password": "Password123!",
            "full_name": "Test Traveller",
        },
    )
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "traveller@example.com", "password": "Password123!"},
    )
    return login_resp.json()["access_token"]


@pytest.fixture(scope="function")
def traveller_headers(traveller_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {traveller_token}"}


@pytest.fixture(scope="function")
def admin_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    """Create an admin user and return authorization header."""
    admin_user = User(
        email="admin@example.com",
        password_hash=hash_password("AdminPassword123!"),
        full_name="System Admin",
        role="admin",
    )
    db_session.add(admin_user)
    db_session.commit()

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "AdminPassword123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def seed_destination(db_session: Session) -> Destination:
    """Create a sample destination with full catalogue for testing."""
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
