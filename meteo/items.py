from datetime import datetime
from typing import Union

from pydantic import BaseModel


class LocationModel(BaseModel):
    city: str
    province: str
    country: str
    latitude: float
    longitude: float


class MetricsModel(BaseModel):
    temperature: float
    relative_humidity: float
    dew_point: float
    apparent_temperature: float
    precipitation: float
    rainfall: float
    snowfall: float
    snow_depth: Union[float, None] = None


class WeatherItem(BaseModel):
    timestamp: datetime
    metrics: MetricsModel


class WeatherModel(BaseModel):
    location: LocationModel
    weather: list[WeatherItem]
