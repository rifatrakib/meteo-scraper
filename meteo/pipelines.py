import json
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
        self.file = Path(f"{settings.TARGET_STORAGE}/{spider.name}/{spider.start_date.date()}.json")
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.touch(exist_ok=True)

    def spider_closed(self, spider):
        if settings.END_STATUS == 429:
            return

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
                    "timestamp": record.timestamp.isoformat(),
                    "temperature": record.metrics.temperature,
                    "relative_humidity": record.metrics.relative_humidity,
                    "dew_point": record.metrics.dew_point,
                    "apparent_temperature": record.metrics.apparent_temperature,
                    "precipitation": record.metrics.precipitation,
                    "rainfall": record.metrics.rainfall,
                    "snowfall": record.metrics.snowfall,
                    "snow_depth": record.metrics.snow_depth,
                },
            )
        return item
