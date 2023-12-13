import scrapy
from scrapy.http import Request


class CitySpider(scrapy.Spider):
    name = "city"
    allowed_domains = ["en.wikipedia.org"]

    def start_requests(self):
        url = "https://en.wikipedia.org/wiki/Lists_of_cities_by_country"
        yield Request(url, callback=self.parse_country_list)

    def parse_country_list(self, response):
        links = response.xpath('//*[@id="mw-content-text"]/div/ul/li/b/a/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.parse_cities_by_country)

    def parse_cities_by_country(self, response):
        print(f"{response.url} got status code {response.status}")
