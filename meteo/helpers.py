import json
from datetime import date, timedelta
from enum import Enum
from functools import lru_cache

from meteo import settings
from meteo.items import LocationModel, MetricsModel, WeatherItem


class Modes(str, Enum):
    """Modes for the weather spider."""

    daily = "daily"
    historical = "historical"


def prepare_daily_mode_query_params(metrics: list[str], locations: list[LocationModel]) -> tuple[dict[str, str], list[LocationModel]]:
    """Prepare the query parameters for the daily mode."""
    cities = []
    start_date = end_date = str(date.today() - timedelta(days=2))
    params = {
        "daily": ",".join(metrics),
        "start_date": start_date,
        "end_date": end_date,
        "latitude": "",
        "longitude": "",
    }

    for location in locations:
        cities.append(location)
        params["latitude"] += f"{location.latitude},"
        params["longitude"] += f"{location.longitude},"

    params["latitude"] = params["latitude"][:-1]
    params["longitude"] = params["longitude"][:-1]
    return params, cities


def prepare_historical_mode_query_params(metrics: list[str], location: LocationModel) -> dict[str, str]:
    """Prepare the query parameters for the historical mode."""
    start_date, end_date = settings.HISTORICAL_DATE_RANGE
    return {
        "daily": ",".join(metrics),
        "start_date": start_date,
        "end_date": end_date,
        "latitude": location.latitude,
        "longitude": location.longitude,
    }


@lru_cache()
def read_locations() -> list[LocationModel]:
    """Build a database of locations from the json file."""
    with open("database/locations.json", encoding="utf-8") as reader:
        countries = json.loads(reader.read())

    locations = []
    for country in countries:
        if country["name"] != settings.TARGET_COUNTRY:
            continue

        for state in country["states"]:
            for city in state["cities"]:
                locations.append(
                    LocationModel(
                        city=city["name"],
                        province=state["name"],
                        country=country["name"],
                        latitude=city["latitude"],
                        longitude=city["longitude"],
                    ),
                )

    return locations


def reshape_weather_data(data) -> list[WeatherItem]:
    """Reshape the weather data into a list of WeatherItem."""
    weather_data = []

    for day, temp, apparent_temp, rain, snow in zip(*data.values()):
        weather_data.append(
            WeatherItem(
                date=day,
                metrics=MetricsModel(
                    temperature=temp,
                    apparent_temperature=apparent_temp,
                    rainfall=rain,
                    snowfall=snow,
                ),
            ),
        )

    return weather_data
