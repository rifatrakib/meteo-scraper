import json
from functools import lru_cache


@lru_cache()
def read_locations():
    """Build a database of locations from the json file."""
    with open("database/locations.json", encoding="utf-8") as reader:
        countries = json.loads(reader.read())

    locations = []
    for country in countries:
        for state in country["states"]:
            locations.extend(state["cities"])

    return locations
