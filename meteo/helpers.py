import json
from datetime import date, timedelta
from functools import lru_cache
from typing import Any, Union

from meteo import settings
from meteo.items import LocationModel, MetricsModel, WeatherItem


def prepare_daily_mode_query_params(
    metrics: list[str],
    locations: list[LocationModel],
    start_date: Union[date, None] = None,
    end_date: Union[date, None] = None,
) -> tuple[dict[str, str], list[LocationModel]]:
    """Prepare the query parameters for the daily mode."""
    cities = []
    if not start_date:
        start_date = end_date = str(date.today() - timedelta(days=2))
    else:
        start_date = str(start_date)
        end_date = str(end_date)

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


def process_stat_output(data: dict[str, Any]) -> dict[str, Any]:
    result = {
        "log_count": {
            "DEBUG": data["log_count/DEBUG"],
            "INFO": data["log_count/INFO"],
        },
        "start_time": data["start_time"],
        "finish_time": data["finish_time"],
        "scheduler": {
            "enqueued": {
                "memory": data["scheduler/enqueued/memory"],
                "total": data["scheduler/enqueued"],
            },
            "dequeued": {
                "memory": data["scheduler/dequeued/memory"],
                "total": data["scheduler/dequeued"],
            },
        },
        "downloader": {
            "request_count": data["downloader/request_count"],
            "request_method_count": {
                "GET": data["downloader/request_method_count/GET"],
            },
            "request_bytes": data["downloader/request_bytes"],
            "response_count": data["downloader/response_count"],
            "response_status_count": {
                "200": data["downloader/response_status_count/200"],
            },
            "response_bytes": data["downloader/response_bytes"],
        },
        "httpcompression": {
            "response_bytes": data["httpcompression/response_bytes"],
            "response_count": data["httpcompression/response_count"],
        },
        "response_received_count": data["response_received_count"],
        "item_scraped_count": data["item_scraped_count"],
        "reason": data["reason"],
    }

    if "downloader/response_status_count/429" in data:
        result["downloader"]["response_status_count"]["429"] = data["downloader/response_status_count/429"]

    return result
