import logging
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models.ai import WeatherSnapshot
from app.db.models.catalogue import Destination
from app.schemas.weather import DailyWeatherForecast, DestinationWeatherResponse

logger = logging.getLogger(__name__)

# Known coordinates for fast deterministic lookup
KNOWN_COORDINATES: Dict[str, Tuple[float, float]] = {
    "mysuru": (12.2958, 76.6394),
    "mysore": (12.2958, 76.6394),
    "kochi": (9.9312, 76.2673),
    "cochin": (9.9312, 76.2673),
    "jaipur": (26.9124, 75.7873),
    "udaipur": (24.5854, 73.7125),
    "goa": (15.2993, 74.1240),
    "panaji": (15.4909, 73.8278),
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "mumbai": (19.0760, 72.8777),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "varanasi": (25.3176, 82.9739),
    "agra": (27.1767, 78.0081),
}

# WMO Weather Code Mappings
WMO_CODE_MAP: Dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def interpret_wmo_code(code: int) -> str:
    return WMO_CODE_MAP.get(code, "Pleasant weather")


def generate_packing_tips(forecasts: List[DailyWeatherForecast]) -> List[str]:
    """Generates rule-based packing suggestions based on temperature and precipitation."""
    tips = ["Government Photo ID & travel documents", "Personal medications & First Aid"]
    if not forecasts:
        return tips + ["Comfortable walking shoes", "All-weather clothing"]

    max_temp = max(f.max_temp_c for f in forecasts)
    min_temp = min(f.min_temp_c for f in forecasts)
    max_precip = max(f.precipitation_probability for f in forecasts)

    if max_precip >= 30:
        tips.append("Compact umbrella or light rain poncho")
        tips.append("Waterproof bag cover or dry pouch")
    if max_temp >= Decimal("30.00"):
        tips.append("Breathable cotton / linen apparel")
        tips.append("UV-protection sunglasses & SPF 50+ sunscreen")
        tips.append("Sun hat or cap")
    elif min_temp <= Decimal("18.00"):
        tips.append("Light jacket, sweater, or fleece layer")
    else:
        tips.append("Comfortable smart-casual travel wear")

    tips.append("Comfortable walking / hiking shoes")
    tips.append("Reusable water bottle")
    return tips


class WeatherService:
    """Service to fetch, normalize, and persist Open-Meteo forecasts with deterministic fallback."""

    def __init__(self):
        self.settings = get_settings()

    def get_destination_weather(
        self,
        db: Session,
        destination: Destination,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> DestinationWeatherResponse:
        """Fetches forecast from Open-Meteo, saves snapshot, or falls back to local fallback."""
        effective_start = start_date or date.today()
        effective_end = end_date or (effective_start + timedelta(days=2))

        # Check if live weather is requested
        if self.settings.weather_provider == "open-meteo":
            try:
                live_response = self._fetch_open_meteo(
                    db=db,
                    destination=destination,
                    start_date=effective_start,
                    end_date=effective_end,
                )
                if live_response:
                    return live_response
            except Exception as exc:
                logger.warning(
                    f"Open-Meteo weather fetch failed for {destination.city}: {exc}. Using fallback."
                )

        # Fallback to local deterministic forecast
        return self._generate_fallback_weather(
            db=db,
            destination=destination,
            start_date=effective_start,
            end_date=effective_end,
        )

    def _get_coordinates(self, destination: Destination) -> Tuple[float, float]:
        city_key = destination.city.lower().strip()
        if city_key in KNOWN_COORDINATES:
            return KNOWN_COORDINATES[city_key]

        # Try geocoding API if unknown city
        try:
            url = f"{self.settings.open_meteo_geocoding_url}/search"
            resp = httpx.get(
                url,
                params={"name": destination.city, "count": 1},
                timeout=self.settings.weather_timeout_seconds,
            )
            if resp.status_code == 200:
                data = resp.json()
                if "results" in data and len(data["results"]) > 0:
                    first = data["results"][0]
                    return float(first["latitude"]), float(first["longitude"])
        except Exception:
            pass

        # Default fallback to Central India coordinates
        return (20.5937, 78.9629)

    def _fetch_open_meteo(
        self,
        db: Session,
        destination: Destination,
        start_date: date,
        end_date: date,
    ) -> Optional[DestinationWeatherResponse]:
        lat, lon = self._get_coordinates(destination)
        url = f"{self.settings.open_meteo_base_url}/forecast"

        # Open-Meteo forecast endpoint
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode",
            "timezone": "auto",
            "start_date": str(start_date),
            "end_date": str(end_date),
        }

        with httpx.Client(timeout=self.settings.weather_timeout_seconds) as client:
            resp = client.get(url, params=params)
            if resp.status_code != 200:
                return None

            data = resp.json()
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            precips = daily.get("precipitation_probability_max", [])
            codes = daily.get("weathercode", [])

            forecasts: List[DailyWeatherForecast] = []
            for i, d_str in enumerate(dates):
                f_date = date.fromisoformat(d_str)
                max_t = Decimal(str(max_temps[i])) if i < len(max_temps) else Decimal("28.00")
                min_t = Decimal(str(min_temps[i])) if i < len(min_temps) else Decimal("20.00")
                avg_t = ((max_t + min_t) / Decimal("2")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                precip = int(precips[i]) if i < len(precips) and precips[i] is not None else 10
                code = int(codes[i]) if i < len(codes) and codes[i] is not None else 1
                cond = interpret_wmo_code(code)

                forecasts.append(
                    DailyWeatherForecast(
                        date=f_date,
                        max_temp_c=max_t,
                        min_temp_c=min_t,
                        avg_temp_c=avg_t,
                        condition=cond,
                        weather_code=code,
                        precipitation_probability=precip,
                        summary=f"{cond}, {min_t}°C to {max_t}°C (Rain prob: {precip}%)",
                    )
                )

            if not forecasts:
                return None

            current_temp = forecasts[0].avg_temp_c
            current_summary = f"{forecasts[0].condition}, {current_temp}°C in {destination.city}"

            # Persist snapshot
            self._persist_snapshot(
                db=db,
                destination_id=destination.id,
                summary=current_summary,
                temperature_c=current_temp,
                provider="open-meteo",
            )

            return DestinationWeatherResponse(
                destination_id=destination.id,
                city=destination.city,
                country=destination.country,
                current_summary=current_summary,
                temperature_c=current_temp,
                observed_at=datetime.now(timezone.utc),
                forecasts=forecasts,
                provider="open-meteo",
                packing_tips=generate_packing_tips(forecasts),
            )

    def _generate_fallback_weather(
        self,
        db: Session,
        destination: Destination,
        start_date: date,
        end_date: date,
    ) -> DestinationWeatherResponse:
        """Deterministic seasonal fallback for offline/test/error resilience."""
        day_count = (end_date - start_date).days + 1
        forecasts: List[DailyWeatherForecast] = []

        base_temp = Decimal("26.00")
        if "goa" in destination.city.lower() or "kochi" in destination.city.lower():
            base_temp = Decimal("29.00")
        elif "jaipur" in destination.city.lower() or "delhi" in destination.city.lower():
            base_temp = Decimal("31.00")

        for d_idx in range(day_count):
            curr_date = start_date + timedelta(days=d_idx)
            max_t = base_temp + Decimal(str(d_idx % 3))
            min_t = base_temp - Decimal("6.00")
            avg_t = ((max_t + min_t) / Decimal("2")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            condition = "Partly cloudy" if d_idx % 2 == 0 else "Sunny & clear"
            precip = 15 if d_idx % 2 == 0 else 5

            forecasts.append(
                DailyWeatherForecast(
                    date=curr_date,
                    max_temp_c=max_t,
                    min_temp_c=min_t,
                    avg_temp_c=avg_t,
                    condition=condition,
                    weather_code=2 if d_idx % 2 == 0 else 0,
                    precipitation_probability=precip,
                    summary=f"{condition}, {min_t}°C to {max_t}°C",
                )
            )

        current_summary = f"{forecasts[0].condition}, {forecasts[0].avg_temp_c}°C (Simulated)"
        self._persist_snapshot(
            db=db,
            destination_id=destination.id,
            summary=current_summary,
            temperature_c=forecasts[0].avg_temp_c,
            provider="mock",
        )

        return DestinationWeatherResponse(
            destination_id=destination.id,
            city=destination.city,
            country=destination.country,
            current_summary=current_summary,
            temperature_c=forecasts[0].avg_temp_c,
            observed_at=datetime.now(timezone.utc),
            forecasts=forecasts,
            provider="mock",
            packing_tips=generate_packing_tips(forecasts),
        )

    def _persist_snapshot(
        self,
        db: Session,
        destination_id: int,
        summary: str,
        temperature_c: Optional[Decimal],
        provider: str,
    ) -> None:
        try:
            snapshot = WeatherSnapshot(
                destination_id=destination_id,
                observed_at=datetime.now(timezone.utc),
                summary=summary[:160],
                temperature_c=temperature_c,
                provider=provider,
            )
            db.add(snapshot)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.warning(f"Failed to persist weather snapshot: {exc}")


_weather_service = WeatherService()


def get_weather_service() -> WeatherService:
    return _weather_service
