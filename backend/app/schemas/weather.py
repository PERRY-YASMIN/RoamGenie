from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DailyWeatherForecast(BaseModel):
    date: date
    max_temp_c: Decimal
    min_temp_c: Decimal
    avg_temp_c: Decimal
    condition: str
    weather_code: int
    precipitation_probability: int
    summary: str

    model_config = ConfigDict(from_attributes=True)


class DestinationWeatherResponse(BaseModel):
    destination_id: int
    city: str
    country: str
    current_summary: str
    temperature_c: Optional[Decimal] = None
    observed_at: datetime
    forecasts: List[DailyWeatherForecast] = Field(default_factory=list)
    provider: str
    packing_tips: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
