import json
from json.decoder import JSONDecodeError
from pathlib import Path

from scrapy import signals

from meteo import settings


class MeteoPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.data = []
        self.file = Path(f"{spider.settings.get('TARGET_STORAGE')}/{spider.name}.json")
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.touch(exist_ok=True)

    def spider_closed(self, spider):
        if settings.END_STATUS == 429:
            return

        try:
            with open(self.file, "r", encoding="utf-8") as reader:
                past_data = json.loads(reader.read())
        except JSONDecodeError:
            past_data = []

        self.data = past_data + self.data
        with open(self.file, "w", encoding="utf-8") as writer:
            writer.write(json.dumps(self.data, indent=4, ensure_ascii=False))

    def process_item(self, item, spider):
        for record in item.weather:
            self.data.append(
                {
                    "city": item.location.city,
                    "province": item.location.province,
                    "country": item.location.country,
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
