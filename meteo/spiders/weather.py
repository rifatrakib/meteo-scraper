import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union
from urllib.parse import urlencode

import scrapy

from meteo import settings
from meteo.helpers import (
    Modes,
    prepare_daily_mode_query_params,
    prepare_historical_mode_query_params,
    process_stat_output,
    read_locations,
    reshape_weather_data,
)
from meteo.items import LocationModel, WeatherModel


class WeatherSpider(scrapy.Spider):
    name = "weather"
    allowed_domains = ["open-meteo.com"]
    handle_httpstatus_list = [429]
    target_endpoint = "https://archive-api.open-meteo.com/v1/archive"
    metrics = ["temperature_2m_mean", "apparent_temperature_mean", "rain_sum", "snowfall_sum"]
    locations: list[LocationModel] = read_locations()

    def __init__(
        self,
        mode: Modes = Modes.daily,
        start_date: Union[str, None] = None,
        end_date: Union[str, None] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if mode not in Modes.__members__.values():
            raise KeyError

        self.mode = mode

        if start_date and end_date:
            self.start_date = datetime.fromisoformat(start_date)
            self.end_date = datetime.fromisoformat(end_date)
            if self.start_date > self.end_date:
                raise ValueError("Start date must be earlier than end date.")
        else:
            self.start_date = datetime.utcnow() - timedelta(days=2)
            self.end_date = self.start_date

    def closed(self, reason):
        logfile = Path(f"{settings.LOG_STORAGE}/{self.name}.json")
        logfile.parent.mkdir(parents=True, exist_ok=True)
        stats = self.crawler.stats.get_stats()
        stats["reason"] = reason
        stats["finish_time"] = datetime.utcnow()

        for key, value in stats.items():
            if isinstance(value, datetime):
                stats[key] = value.isoformat()

        with open(logfile, "w") as writer:
            writer.write(json.dumps(process_stat_output(stats), indent=4))

    def start_requests(self):
        if self.mode == Modes.daily:
            for index in range(0, len(self.locations), 10):
                params, cities = prepare_daily_mode_query_params(
                    self.metrics,
                    self.locations[index : index + 10],
                    self.start_date.date(),
                    self.end_date.date(),
                )

                yield scrapy.Request(
                    f"{self.target_endpoint}?{urlencode(params)}",
                    callback=self.parse,
                    cb_kwargs={"location": cities},
                )
        else:
            for location in self.locations:
                params = prepare_historical_mode_query_params(self.metrics, location)
                yield scrapy.Request(
                    f"{self.target_endpoint}?{urlencode(params)}",
                    callback=self.parse,
                    cb_kwargs={"location": location},
                )

    def parse(self, response, **kwargs):
        if response.status == 429:
            data = response.json()
            self.crawler.engine.close_spider(self, reason=data["reason"])
            return

        data = response.json()
        if self.mode == Modes.daily:
            for index, item in enumerate(data):
                yield WeatherModel(
                    location=kwargs.get("location")[index],
                    weather=reshape_weather_data(item["daily"]),
                )
        else:
            yield WeatherModel(
                location=kwargs.get("location"),
                weather=reshape_weather_data(data["daily"]),
            )
