from datetime import date, timedelta
from urllib.parse import urlencode

import scrapy

from meteo import settings
from meteo.helpers import read_locations, reshape_weather_data
from meteo.items import LocationModel, WeatherModel


class WeatherSpider(scrapy.Spider):
    name = "weather"
    allowed_domains = ["open-meteo.com"]
    target_endpoint = "https://archive-api.open-meteo.com/v1/archive"
    metrics = ["temperature_2m_mean", "apparent_temperature_mean", "rain_sum", "snowfall_sum"]
    locations: list[LocationModel] = read_locations()

    def __init__(self, is_daily: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_daily = is_daily

    def start_requests(self):
        params = {"daily": ",".join(self.metrics), "latitude": "", "longitude": ""}
        if self.is_daily:
            start_date = end_date = str(date.today() - timedelta(days=2))
            params.update({"start_date": start_date, "end_date": end_date})
            cities = []

            for index, location in enumerate(self.locations):
                cities.append(location)
                params["latitude"] += f"{location.latitude},"
                params["longitude"] += f"{location.longitude},"

                if (index + 1) % 10 == 0:
                    params["latitude"] = params["latitude"][:-1]
                    params["longitude"] = params["longitude"][:-1]

                    yield scrapy.Request(
                        f"{self.target_endpoint}?{urlencode(params)}",
                        callback=self.parse,
                        cb_kwargs={"location": cities},
                    )

                    params["latitude"] = ""
                    params["longitude"] = ""
                    cities = []
        else:
            start_date, end_date = settings.HISTORICAL_DATE_RANGE
            for location in self.locations:
                params.update({"latitude": location.latitude, "longitude": location.longitude})
                yield scrapy.Request(
                    f"{self.target_endpoint}?{urlencode(params)}",
                    callback=self.parse,
                    cb_kwargs={"location": location},
                )

    def parse(self, response, **kwargs):
        print(f"{response.status = }")
        data = response.json()
        if self.is_daily:
            for index, item in enumerate(data):
                print(f"{item = }")
                yield WeatherModel(
                    location=kwargs.get("location")[index],
                    weather=reshape_weather_data(item["daily"]),
                )
        else:
            yield WeatherModel(
                location=kwargs.get("location"),
                weather=reshape_weather_data(data["daily"]),
            )
