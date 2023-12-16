import scrapy


class LocationSpider(scrapy.Spider):
    name = "location"
    allowed_domains = ["geocoding-api.open-meteo.com"]

    def start_requests(self):
        yield scrapy.Request(
            "https://geocoding-api.open-meteo.com/v1/search?name=Comilla",
            callback=self.parse,
        )

    def parse(self, response):
        print(response.json())
