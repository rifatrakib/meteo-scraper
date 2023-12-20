from datetime import datetime

from pydantic import BaseModel, ConfigDict, validator


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.strftime("%Y-%m-%d"),
        },
    )


class LocationModel(BaseSchema):
    city_name: str
    country_name: str
    latitude: float
    longitude: float


class MetricsModel(BaseSchema):
    temperature: float
    apparent_temperature: float
    rainfall: float
    snowfall: float


class WeatherItem(BaseSchema):
    date: datetime
    metrics: MetricsModel

    @validator("date", pre=True)
    def process_timestamp(cls, value):
        return datetime(*map(int, value.split("-")))


class WeatherModel(BaseSchema):
    location: LocationModel
    weather: list[WeatherItem]
