from fastapi.testclient import TestClient
from app.config import get_settings
from app.db.session import database_status, get_engine
from app.main import app

client = TestClient(app)

def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["application"] == "online"
    assert response.json()["database"] in {"connected", "not_configured", "unavailable"}

def test_mock_plan_is_structured() -> None:
    response = client.post("/api/v1/plans/preview", json={"starting_location":"Chennai","destination":"Mysuru","start_date":"2026-08-10","end_date":"2026-08-12","travellers":2,"total_budget":"20000.00","preferences":["heritage","food"]})
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert len(body["days"]) == 3
    assert body["estimated_total"] == "20000.00"

def test_invalid_dates_fail_validation() -> None:
    response = client.post("/api/v1/plans/preview", json={"starting_location":"Chennai","destination":"Mysuru","start_date":"2026-08-12","end_date":"2026-08-10","travellers":2,"total_budget":"20000.00"})
    assert response.status_code == 422

def test_invalid_database_url_is_reported_safely(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "not-a-connection-url")
    get_settings.cache_clear()
    get_engine.cache_clear()
    try:
        assert database_status() == "unavailable"
    finally:
        get_engine.cache_clear()
        get_settings.cache_clear()
