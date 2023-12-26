import json
import subprocess
from datetime import datetime, timedelta

from meteo import settings


def start_daily_scraper():
    try:
        with open("database/downloads/weather.json", encoding="utf-8") as reader:
            data = json.loads(reader.read())

        latest_date = datetime.fromisoformat(data[-1]["date"])
        next_date = latest_date + timedelta(days=1)
    except Exception:
        next_date = datetime.fromisoformat(settings.HISTORICAL_DATE_RANGE[0])

    next_date = next_date.strftime("%Y-%m-%d")
    arguments = f"-a mode=daily -a start_date={next_date} -a end_date={next_date}"
    command = f"scrapy crawl weather {arguments}"
    print(command)

    subprocess.run(command, shell=True)


if __name__ == "__main__":
    start_daily_scraper()
