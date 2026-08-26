from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.ai import WeatherSnapshot
from app.db.models.catalogue import Destination
from app.services.weather_service import (
    WeatherService,
    generate_packing_tips,
    interpret_wmo_code,
)


@pytest.fixture
def weather_destination(db_session: Session) -> Destination:
    dest = Destination(
        city="Goa",
        country="India",
        description="Coastal Paradise",
        average_daily_cost=Decimal("5000.00"),
        active=True,
    )
    db_session.add(dest)
    db_session.commit()
    db_session.refresh(dest)
    return dest


def test_interpret_wmo_codes():
    """Verify correct text condition mapping for WMO weather codes."""
    assert interpret_wmo_code(0) == "Clear sky"
    assert interpret_wmo_code(2) == "Partly cloudy"
    assert interpret_wmo_code(61) == "Slight rain"
    assert interpret_wmo_code(95) == "Thunderstorm"
    assert interpret_wmo_code(999) == "Pleasant weather"


def test_packing_tips_generator():
    """Verify weather-aware packing suggestions."""
    from app.schemas.weather import DailyWeatherForecast

    hot_forecast = [
        DailyWeatherForecast(
            date=date(2026, 9, 1),
            max_temp_c=Decimal("34.00"),
            min_temp_c=Decimal("26.00"),
            avg_temp_c=Decimal("30.00"),
            condition="Clear sky",
            weather_code=0,
            precipitation_probability=10,
            summary="Sunny & hot",
        )
    ]
    hot_tips = generate_packing_tips(hot_forecast)
    assert any("sunscreen" in t.lower() or "sunglasses" in t.lower() for t in hot_tips)
    assert any("cotton" in t.lower() for t in hot_tips)

    rainy_forecast = [
        DailyWeatherForecast(
            date=date(2026, 9, 1),
            max_temp_c=Decimal("25.00"),
            min_temp_c=Decimal("22.00"),
            avg_temp_c=Decimal("23.50"),
            condition="Heavy rain",
            weather_code=65,
            precipitation_probability=85,
            summary="Heavy rain showers",
        )
    ]
    rain_tips = generate_packing_tips(rainy_forecast)
    assert any("umbrella" in t.lower() or "poncho" in t.lower() for t in rain_tips)


def test_fetch_live_open_meteo_mocked(db_session: Session, weather_destination: Destination):
    """Test successful Open-Meteo fetch and database snapshot persistence using mocked HTTP."""
    mock_payload = {
        "daily": {
            "time": ["2026-09-15", "2026-09-16"],
            "temperature_2m_max": [31.5, 32.0],
            "temperature_2m_min": [24.0, 24.5],
            "precipitation_probability_max": [20, 45],
            "weathercode": [1, 61],
        }
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch("httpx.Client.get", return_value=mock_resp):
        service = WeatherService()
        result = service.get_destination_weather(
            db=db_session,
            destination=weather_destination,
            start_date=date(2026, 9, 15),
            end_date=date(2026, 9, 16),
        )

        assert result.city == "Goa"
        assert result.provider == "open-meteo"
        assert len(result.forecasts) == 2
        assert result.forecasts[0].max_temp_c == Decimal("31.5")
        assert result.forecasts[1].condition == "Slight rain"

        # Verify WeatherSnapshot record in database
        snapshots = db_session.query(WeatherSnapshot).filter(
            WeatherSnapshot.destination_id == weather_destination.id
        ).all()
        assert len(snapshots) >= 1
        assert snapshots[0].provider == "open-meteo"


def test_weather_fallback_on_network_error(db_session: Session, weather_destination: Destination):
    """Test graceful fallback when Open-Meteo API is unreachable or times out."""
    with patch("httpx.Client.get", side_effect=Exception("Connection timed out")):
        service = WeatherService()
        result = service.get_destination_weather(
            db=db_session,
            destination=weather_destination,
            start_date=date(2026, 9, 15),
            end_date=date(2026, 9, 17),
        )

        assert result.city == "Goa"
        assert result.provider == "mock"
        assert len(result.forecasts) == 3
        assert result.forecasts[0].avg_temp_c > Decimal("0.00")


def test_destination_weather_api_endpoint(client: TestClient, weather_destination: Destination):
    """Test GET /api/v1/destinations/{id}/weather."""
    response = client.get(f"/api/v1/destinations/{weather_destination.id}/weather")
    assert response.status_code == 200
    data = response.json()
    assert data["destination_id"] == weather_destination.id
    assert data["city"] == "Goa"
    assert len(data["forecasts"]) > 0
    assert len(data["packing_tips"]) > 0
