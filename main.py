import json
import subprocess
import time
from datetime import datetime, timedelta

from meteo import settings


def start_daily_scraper(today: bool = False):
    if today:
        command = "scrapy crawl weather -a mode=daily"
    else:
        try:
            with open("database/downloads/weather.json", encoding="utf-8") as reader:
                data = json.loads(reader.read())

            latest_date = datetime.fromisoformat(data[-1]["date"])
            next_date = latest_date - timedelta(days=1)
        except Exception:
            next_date = datetime.fromisoformat(settings.HISTORICAL_DATE_RANGE[0])

        next_date = next_date.strftime("%Y-%m-%d")
        arguments = f"-a mode=daily -a start_date={next_date} -a end_date={next_date}"
        command = f"scrapy crawl weather {arguments}"

    print(command)
    subprocess.run(command, shell=True)


if __name__ == "__main__":
    start_daily_scraper(today=True)

    while True:
        start_daily_scraper()
        time.sleep(5)

        try:
            with open("database/logs/weather.json") as reader:
                stats = json.loads(reader.read())

            finish_time = datetime.fromisoformat(stats["finish_time"])
            if finish_time.date() != datetime.utcnow().date():
                continue
            if "Hourly" in stats["reason"]:
                print(stats["reason"])
                print("Sleeping for an hour...")
                time.sleep(3600)
            elif "Daily" in stats["reason"]:
                print(stats["reason"])
                print("Stopping for today...")
                break
        except Exception:
            pass
