import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

from meteo import settings


def start_daily_scraper(today: bool = False):
    command = "scrapy crawl weather"
    log_file = f"{(datetime.utcnow() - timedelta(days=2)).date()}.log"

    if not today:
        files = [file.name.replace(".json", "") for file in Path(f"{settings.TARGET_STORAGE}/weather").glob("**/*.json") if file.is_file()]
        latest_date = datetime.fromisoformat(files[0])
        next_date = latest_date - timedelta(days=1)
        next_date = next_date.date()
        arguments = f"-a start_date={next_date} -a end_date={next_date}"
        command = f"scrapy crawl weather {arguments}"
        log_file = f"{next_date}.log"

    location = Path(f"{settings.LOGS_STORAGE}/weather")
    Path(location).mkdir(parents=True, exist_ok=True)
    command += f" 2>&1 | tee {location}/{log_file}"

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
            current_time = datetime.utcnow()

            if finish_time.date() != current_time.date():
                continue

            if "Hourly" in stats["reason"]:
                print(stats["reason"])
                print("Sleeping till the next hour...")
                nxt = current_time.replace(hour=current_time.hour + 1, minute=0, second=0, microsecond=0)
                time.sleep((nxt - current_time).seconds + 1)
            elif "Daily" in stats["reason"]:
                print(stats["reason"])
                print("Stopping for today...")
                break
        except Exception:
            pass
