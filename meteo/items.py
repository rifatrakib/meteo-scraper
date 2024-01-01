from datetime import datetime
from typing import Union

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%d"),
        },
    )


class LocationModel(BaseSchema):
    city: str
    province: str
    country: str
    latitude: float
    longitude: float


class MetricsModel(BaseSchema):
    temperature: float
    relative_humidity: float
    dew_point: float
    apparent_temperature: float
    precipitation: float
    rainfall: float
    snowfall: float
    snow_depth: Union[float, None] = None


class WeatherItem(BaseSchema):
    timestamp: datetime
    metrics: MetricsModel


class WeatherModel(BaseSchema):
    location: LocationModel
    weather: list[WeatherItem]
