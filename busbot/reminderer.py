"""Functions for comparing old/new bus data and checking reminder status
"""

# https://github.com/alifeee/bus_bot/issues/1

import datetime
import json
import logging
from telegram import *
from telegram.ext import *


from .busapi import get_all_journeys, get_journey_capacities, Credentials
from .journey import Journey
from .stop import Stop

credentials = Credentials("credentials.json")

# compare 2 journeys (old, new)
# find journey from journeys and journey_id
# for list of journeys (journey, start/end stop), get true/false if it has capacity where it did not before or vice versa

_NO_LONGER_EXISTS_MESSAGE = """
A journey you were tracking {message}

{journey}

It has been removed.

Use /track to enable/disable tracking.
For capacity information, use /timetable.
"""

_TRACKED_MESSAGE = """
A journey you were tracking {message}

{journey}

It went from {seats_before} seats to {seats_after} seats.

Use /track to enable/disable tracking.
For capacity information, use /timetable.
"""


def _get_stop_by_id(stops: list[Stop], stop_id: str) -> Stop:
    for stop in stops:
        if stop.stop_id == stop_id:
            return stop
    return None


def _get_journey_by_id(journeys: list[Journey], journey_id: str) -> Journey:
    for journey in journeys:
        if journey.journey_id == journey_id:
            return journey
    return None


def _format_journey_nicely(journey: Journey, start_stop_id: str, end_stop_id: str):
    return "{dayandtime}: {journeytype}".format(
        dayandtime=get_start_time_of_stop(journey, start_stop_id, end_stop_id).strftime(
            "%A %d/%m %H:%M"
        ),
        journeytype=journey.type,
    )


def get_start_time_of_stop(
    journey: Journey, start_stop_id: str, end_stop_id: str
) -> datetime.datetime:
    if journey.type == "OUTBOUND":
        return _get_stop_by_id(journey.stops, start_stop_id).journey_stop_time
    else:
        return _get_stop_by_id(journey.stops, end_stop_id).journey_stop_time


def has_changed_capacity(journey1, journey2):
    raise NotImplementedError


def initialise_job(job_queue: JobQueue):
    job_queue.run_repeating(
        _check_capacity,
        interval=datetime.timedelta(minutes=15),
        first=0,
        name="check_capacity",
    )
    job_queue.run_once(
        _check_capacity,
        when=0,
    )


async def _check_capacity(context: ContextTypes.DEFAULT_TYPE):
    bot_data = context.bot_data

    with open("historical_capacities.json", "r", encoding="utf-8") as file:
        historical_capacities = json.load(file)

    logger = logging.getLogger(__name__)

    for user_id, data in bot_data.items():
        logger.info("Checking capacity for user %s", user_id)

        start_stop_id = data["start_stop_id"]
        end_stop_id = data["end_stop_id"]
        tracked_journey_ids = [
            journey_id for journey_id in data.get("tracked_journeys", [])
        ]

        # get all journeys
        all_journeys = get_all_journeys(credentials.pass_id)

        tracked_journeys = []
        for tracked_journey_id in tracked_journey_ids:
            tracked_journey = _get_journey_by_id(all_journeys, tracked_journey_id)
            if tracked_journey is None:
                # journey no longer exists
                await context.bot.send_message(
                    chat_id=user_id,
                    text=_NO_LONGER_EXISTS_MESSAGE.format(
                        message="no longer exists",
                        journey=tracked_journey_id,
                    ),
                )
                context.bot_data[user_id]["tracked_journeys"].remove(tracked_journey_id)

                # chat = await context.bot.get_chat(user_id)
                # print(chat.first_name)

                continue

            # get capacities
            if start_stop_id not in [s.stop_id for s in tracked_journey.stops]:
                raise ValueError("Start stop not in journey")
            if end_stop_id not in [s.stop_id for s in tracked_journey.stops]:
                raise ValueError("End stop not in journey")

            if tracked_journey.type == "OUTBOUND":
                start_stop = _get_stop_by_id(tracked_journey.stops, start_stop_id)
                end_stop = _get_stop_by_id(tracked_journey.stops, end_stop_id)
            elif tracked_journey.type == "RETURN":
                start_stop = _get_stop_by_id(tracked_journey.stops, end_stop_id)
                end_stop = _get_stop_by_id(tracked_journey.stops, start_stop_id)

            tracked_journey.start_stop = start_stop
            tracked_journey.end_stop = end_stop

            tracked_journeys.append(tracked_journey)

        logger.info("Found %d tracked journeys", len(tracked_journeys))
        if len(tracked_journeys) == 0:
            continue

        capacities = get_journey_capacities(tracked_journeys)

        # compare capacities
        for journey_id, capacity in capacities.items():
            journey = _get_journey_by_id(all_journeys, journey_id)
            if journey_id not in historical_capacities:
                historical_capacities[journey_id] = capacity
                continue

            last_capacity = historical_capacities[journey_id]

            if last_capacity <= 0 and capacity <= 0:
                continue
            elif last_capacity <= 0 and capacity > 0:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=_TRACKED_MESSAGE.format(
                        message="has capacity now!",
                        journey=_format_journey_nicely(
                            journey, start_stop_id, end_stop_id
                        ),
                        seats_before=last_capacity,
                        seats_after=capacity,
                    ),
                )
            elif last_capacity > 0 and capacity <= 0:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=_TRACKED_MESSAGE.format(
                        message="is full now :(",
                        journey=_format_journey_nicely(
                            journey, start_stop_id, end_stop_id
                        ),
                        seats_before=last_capacity,
                        seats_after=capacity,
                    ),
                )
            elif last_capacity > 0 and capacity > 0:
                continue

            historical_capacities[journey_id] = capacity

    with open("historical_capacities.json", "w", encoding="utf-8") as file:
        json.dump(historical_capacities, file, indent=4)
