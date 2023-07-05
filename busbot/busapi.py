"""Functions for grabbing journey data from the API.
"""

import datetime
import json

from stop import Stop
from journey import Journey

import requests

ELIGIBLE_JOURNEYS_URL = (
    "https://app.zeelo.co/api/travels/{pass_id}/elegible-journey-groups"
)

DATETIME_FORMAT = "%Y%m%d%H%M%S Europe/London"


class Credentials:
    """Credentials for the API"""

    def __init__(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as file:
            credentials = json.load(file)
        self.pass_id = credentials["PASS_ID"]
        self.market_id = credentials["MARKET_ID"]
        self.business_id = credentials["BUSINESS_ID"]
        self.tier_id = credentials["TIER_ID"]
        self.authorization = credentials["AUTHORIZATION"]


def get_all_journeys(pass_id: str) -> list[Journey]:
    """Get all journeys for a pass id"""
    url = ELIGIBLE_JOURNEYS_URL.format(pass_id=pass_id)
    response = requests.get(url, timeout=5)
    response.raise_for_status()

    result = json.loads(response.text)

    if result["total_pages"] != 1:
        raise NotImplementedError("More than one page of journeys")

    journeys_per_day = result["data"]

    journeys = []

    for day in journeys_per_day:
        for journey in day["journeys"]:
            stops = []
            for stop in journey["journey"]["journey_stops"]:
                stop_time = datetime.datetime.strptime(
                    stop["departure_datetime"], DATETIME_FORMAT
                )
                stops.append(
                    Stop(
                        stop_id=stop["location"]["stop_id"],
                        name=stop["location"]["stop_name"],
                        journey_stop_id=stop["journey_stop_id"],
                        journey_stop_time=stop_time,
                    )
                )
            # do not include time in the date
            start_date = datetime.datetime.strptime(
                journey["start_date"], DATETIME_FORMAT
            ).date()
            journeys.append(
                Journey(
                    journey_id=journey["id"],
                    type=journey["journey"]["journey_type"],
                    stops=stops,
                    day=start_date,
                )
            )

    return journeys


if __name__ == "__main__":
    creds = Credentials("credentials.json")
    all_journeys = get_all_journeys(creds.pass_id)
    print(all_journeys)
