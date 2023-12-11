import scrapy


class WeatherSpider(scrapy.Spider):
    name = "weather"
    allowed_domains = ["open-meteo.com"]

    def start_requests(self):
        yield scrapy.Request(
            "https://api.open-meteo.com/v1/forecast?latitude=23.4619&longitude=91.185&hourly=temperature_2m",
            callback=self.parse,
        )

    def parse(self, response):
        yield response.json()
