import scrapy


class WeatherSpider(scrapy.Spider):
    name = "weather"
    allowed_domains = ["open-meteo.com"]
    start_urls = ["https://open-meteo.com/en/docs"]

    def parse(self, response):
        pass
