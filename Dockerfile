FROM python:3.9-slim-buster

WORKDIR /meteo-scraper

COPY requirements.txt /meteo-scraper/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /meteo-scraper/requirements.txt

COPY ./meteo /meteo-scraper/meteo
COPY ./main.py /meteo-scraper/main.py
COPY ./scrapy.cfg /meteo-scraper/scrapy.cfg
COPY ./database/locations.json /meteo-scraper/database/locations.json

CMD ["python", "main.py"]
