import json
from functools import lru_cache

from meteo import settings
from meteo.items import LocationModel, MetricsModel, WeatherItem


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
