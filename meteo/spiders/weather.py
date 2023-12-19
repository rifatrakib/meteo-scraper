from urllib.parse import urlencode

import scrapy

from meteo.helpers import read_locations


class WeatherSpider(scrapy.Spider):
    name = "weather"
    allowed_domains = ["open-meteo.com"]
    target_endpoint = "https://archive-api.open-meteo.com/v1/archive"
    locations = read_locations()

    def start_requests(self):
        params = {
            "start_date": "1940-01-01",
            "end_date": "2023-11-30",
            "hourly": "temperature_2m",
        }

        for city in self.locations:
            params.update({"latitude": city["latitude"], "longitude": city["longitude"]})
            yield scrapy.Request(
                f"{self.target_endpoint}?{urlencode(params)}",
                callback=self.parse,
            )

    def parse(self, response):
        print(response.status)
