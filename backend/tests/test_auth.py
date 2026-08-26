from datetime import datetime, timedelta, timezone
import jwt
from fastapi.testclient import TestClient

from app.config import get_settings
from app.services.auth_service import create_access_token

settings = get_settings()


# ============================================================================
# USER REGISTRATION
# ============================================================================


def test_register_success(client: TestClient) -> None:
    """Verify that new user registration succeeds with correct fields and role."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "traveller"
    assert "id" in data
    assert "password_hash" not in data  # Never expose password hash


def test_register_duplicate_email(client: TestClient) -> None:
    """Verify that registering with an already existing email returns 409 Conflict."""
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongPassword123!",
        "full_name": "First User",
    }
    client.post("/api/v1/auth/register", json=payload)
    # Attempt second registration with same email
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_register_short_password_fails_validation(client: TestClient) -> None:
    """Verify that short passwords fail Pydantic validation with 422."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "shortpw@example.com",
            "password": "short",
            "full_name": "Short Pw",
        },
    )
    assert response.status_code == 422


# ============================================================================
# USER LOGIN & CREDENTIAL VERIFICATION
# ============================================================================


def test_login_success(client: TestClient) -> None:
    """Verify that valid credentials return a signed JWT token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "logintest@example.com",
            "password": "CorrectPassword123!",
            "full_name": "Login Test",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "logintest@example.com", "password": "CorrectPassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["email"] == "logintest@example.com"
    assert data["role"] == "traveller"
    assert len(data["access_token"]) > 20


def test_login_case_insensitive_email(client: TestClient) -> None:
    """Verify that email login is case-insensitive."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "caseuser@example.com",
            "password": "CorrectPassword123!",
            "full_name": "Case User",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "CASEUSER@EXAMPLE.COM", "password": "CorrectPassword123!"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "caseuser@example.com"


def test_login_invalid_password(client: TestClient) -> None:
    """Verify that incorrect password returns 401 Unauthorized."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpw@example.com",
            "password": "CorrectPassword123!",
            "full_name": "Wrong Pw",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_user(client: TestClient) -> None:
    """Verify that non-existent email returns 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "Password123!"},
    )
    assert response.status_code == 401


# ============================================================================
# JWT TOKEN VALIDATION & SECURITY EDGE CASES
# ============================================================================


def test_unauthenticated_request_rejected(client: TestClient) -> None:
    """Verify that missing Authorization header returns 401 Unauthorized."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert "Authentication token required" in str(response.json())


def test_empty_and_whitespace_bearer_token_rejected(client: TestClient) -> None:
    """Verify that empty or whitespace-only Bearer tokens return 401 Unauthorized."""
    r1 = client.get("/api/v1/users/me", headers={"Authorization": "Bearer "})
    assert r1.status_code == 401

    r2 = client.get("/api/v1/users/me", headers={"Authorization": "Bearer     "})
    assert r2.status_code == 401


def test_invalid_and_malformed_token_rejected(client: TestClient) -> None:
    """Verify that malformed JWT strings return 401 Unauthorized."""
    r1 = client.get("/api/v1/users/me", headers={"Authorization": "Bearer not-a-valid-token"})
    assert r1.status_code == 401
    assert "Invalid authentication credentials" in str(r1.json())

    r2 = client.get("/api/v1/users/me", headers={"Authorization": "Bearer eyJhbGciOi.corrupted.payload"})
    assert r2.status_code == 401


def test_forged_token_with_wrong_secret_rejected(client: TestClient) -> None:
    """Verify that tokens signed with an unauthorized secret key return 401 Unauthorized."""
    now = datetime.now(timezone.utc)
    forged_payload = {
        "sub": "1",
        "email": "forged@example.com",
        "role": "admin",
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "iat": int(now.timestamp()),
    }
    forged_token = jwt.encode(forged_payload, "completely_wrong_secret_key", algorithm="HS256")
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {forged_token}"})
    assert response.status_code == 401
    assert "Invalid authentication credentials" in str(response.json())


def test_expired_token_rejected(client: TestClient) -> None:
    """Verify that expired JWT tokens return 401 Unauthorized with token expired detail."""
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "1",
        "email": "traveller@example.com",
        "role": "traveller",
        "exp": int((now - timedelta(minutes=10)).timestamp()),
        "iat": int((now - timedelta(minutes=40)).timestamp()),
    }
    expired_token = jwt.encode(expired_payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401
    assert "Token has expired" in str(response.json())


def test_token_for_nonexistent_user_rejected(client: TestClient) -> None:
    """Verify that a valid token whose user ID no longer exists in DB returns 401."""
    nonexistent_token = create_access_token(user_id=99999, email="ghost@example.com", role="traveller")
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {nonexistent_token}"})
    assert response.status_code == 401
    assert "no longer exists" in str(response.json())


# ============================================================================
# USER PROFILE & PREFERENCES ISOLATION
# ============================================================================


def test_get_current_user_profile(
    client: TestClient, traveller_headers: dict[str, str]
) -> None:
    """Verify retrieving current user profile."""
    response = client.get("/api/v1/users/me", headers=traveller_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "traveller@example.com"
    assert data["full_name"] == "Test Traveller"
    assert data["role"] == "traveller"
    assert "password_hash" not in data


def test_user_preferences_lifecycle(
    client: TestClient, traveller_headers: dict[str, str]
) -> None:
    """Verify user preferences update and retrieval."""
    pref_payload = {
        "hotel_preference": "luxury",
        "food_preference": "vegetarian",
        "transport_preference": "train",
        "travel_style": "relaxed",
        "special_requirements": "Wheelchair accessible",
        "activities": ["heritage", "culinary", "museums"],
    }
    update_resp = client.put(
        "/api/v1/users/me/preferences",
        json=pref_payload,
        headers=traveller_headers,
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["hotel_preference"] == "luxury"
    assert updated["food_preference"] == "vegetarian"
    assert set(updated["activities"]) == {"heritage", "culinary", "museums"}

    get_resp = client.get(
        "/api/v1/users/me/preferences", headers=traveller_headers
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["hotel_preference"] == "luxury"
    assert set(get_resp.json()["activities"]) == {"heritage", "culinary", "museums"}


def test_cross_user_preferences_isolation(client: TestClient) -> None:
    """Verify that User A updating preferences has zero effect on User B preferences."""
    # Register User A & User B
    client.post("/api/v1/auth/register", json={"email": "usera_pref@example.com", "password": "Password123!", "full_name": "User A"})
    client.post("/api/v1/auth/register", json={"email": "userb_pref@example.com", "password": "Password123!", "full_name": "User B"})

    login_a = client.post("/api/v1/auth/login", json={"email": "usera_pref@example.com", "password": "Password123!"})
    login_b = client.post("/api/v1/auth/login", json={"email": "userb_pref@example.com", "password": "Password123!"})

    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    # User A sets preferences to luxury & photography
    client.put("/api/v1/users/me/preferences", json={"hotel_preference": "luxury", "food_preference": "vegan", "transport_preference": "flight", "travel_style": "fast", "special_requirements": "", "activities": ["photography"]}, headers=headers_a)

    # User B sets preferences to budget & culinary
    client.put("/api/v1/users/me/preferences", json={"hotel_preference": "budget", "food_preference": "non-vegetarian", "transport_preference": "bus", "travel_style": "relaxed", "special_requirements": "", "activities": ["culinary"]}, headers=headers_b)

    # Verify User A preferences
    resp_a = client.get("/api/v1/users/me/preferences", headers=headers_a)
    assert resp_a.json()["hotel_preference"] == "luxury"
    assert resp_a.json()["activities"] == ["photography"]

    # Verify User B preferences remain budget & culinary
    resp_b = client.get("/api/v1/users/me/preferences", headers=headers_b)
    assert resp_b.json()["hotel_preference"] == "budget"
    assert resp_b.json()["activities"] == ["culinary"]
