import json
import subprocess
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from meteo import settings


def start_daily_scraper(today: bool = False):
    command = "scrapy crawl weather"

    if not today:
        with open(f"{settings.TARGET_STORAGE}/weather.json", encoding="utf-8") as reader:
            data = json.loads(reader.read())

        latest_date = datetime.fromisoformat(data[-1]["timestamp"])
        next_date = latest_date - timedelta(days=1)
        next_date = next_date.date()
        arguments = f"-a start_date={next_date} -a end_date={next_date}"
        command = f"scrapy crawl weather {arguments}"

    location = Path(f"{settings.LOGS_STORAGE}/weather")
    Path(location).mkdir(parents=True, exist_ok=True)
    command += f" 2>&1 | tee {location}/{date.today()}.log"

    print(command)
    subprocess.run(command, shell=True)


if __name__ == "__main__":
    start_daily_scraper(today=True)

    while True:
        start_daily_scraper()
        time.sleep(5)

        try:
            with open(f"{settings.STATS_STORAGE}/weather.json") as reader:
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
