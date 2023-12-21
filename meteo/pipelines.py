import json
from pathlib import Path

from scrapy import signals


class MeteoPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.data = []
        self.target_storage = spider.settings.get("TARGET_STORAGE")
        Path(self.target_storage).mkdir(parents=True, exist_ok=True)

    def spider_closed(self, spider):
        filename = f"{self.target_storage}/{spider.name}.json"
        with open(filename, "r", encoding="utf-8") as reader:
            past_data = json.loads(reader.read())

        self.data = past_data + self.data
        with open(filename, "w", encoding="utf-8") as writer:
            writer.write(json.dumps(self.data, indent=4, ensure_ascii=False))

    def process_item(self, item, spider):
        for record in item.weather:
            self.data.append(
                {
                    "city_name": item.location.city_name,
                    "country_name": item.location.country_name,
                    "latitude": item.location.latitude,
                    "longitude": item.location.longitude,
                    "date": record.date.strftime("%Y-%m-%d"),
                    "temperature": record.metrics.temperature,
                    "apparent_temperature": record.metrics.apparent_temperature,
                    "rainfall": record.metrics.rainfall,
                    "snowfall": record.metrics.snowfall,
                },
            )
        return item
