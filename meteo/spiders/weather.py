from urllib.parse import urlencode

import scrapy

from meteo.helpers import read_locations, reshape_weather_data
from meteo.items import LocationModel, WeatherModel


class WeatherSpider(scrapy.Spider):
    name = "weather"
    allowed_domains = ["open-meteo.com"]
    target_endpoint = "https://archive-api.open-meteo.com/v1/archive"
    metrics = ["temperature_2m_mean", "apparent_temperature_mean", "rain_sum", "snowfall_sum"]
    locations: list[LocationModel] = read_locations()

    def start_requests(self):
        params = {
            "start_date": "2023-01-01",
            "end_date": "2023-11-30",
            "daily": ",".join(self.metrics),
        }

        for location in self.locations:
            params.update({"latitude": location.latitude, "longitude": location.longitude})
            yield scrapy.Request(
                f"{self.target_endpoint}?{urlencode(params)}",
                callback=self.parse,
                cb_kwargs={"location": location},
            )

    def parse(self, response, **kwargs):
        data = response.json()
        yield WeatherModel(
            location=kwargs.get("location"),
            weather=reshape_weather_data(data["daily"]),
        )
