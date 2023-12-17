import scrapy

from meteo.settings import CITIES as cities


class LocationSpider(scrapy.Spider):
    name = "location"
    allowed_domains = ["geocoding-api.open-meteo.com"]

    def start_requests(self):
        for city in cities:
            yield scrapy.Request(
                f"https://geocoding-api.open-meteo.com/v1/search?name={city}",
                callback=self.parse,
            )

    def parse(self, response):
        data = response.json()
        if "results" in data and data["results"]:
            lat = data["results"][0]["latitude"] if "latitude" in data["results"][0] else 0.000
            lon = data["results"][0]["longitude"] if "longitude" in data["results"][0] else 0.000
            print(lat, lon)
