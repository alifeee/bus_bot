"""Functions for comparing old/new bus data and checking reminder status
"""

# https://github.com/alifeee/bus_bot/issues/1

import datetime
from telegram import *
from telegram.ext import *

from .busapi import get_all_journeys, get_journey_capacities, Credentials
from .journey import Journey

credentials = Credentials("credentials.json")

# compare 2 journeys (old, new)
# find journey from journeys and journey_id
# for list of journeys (journey, start/end stop), get true/false if it has capacity where it did not before or vice versa


def _get_journey_by_id(journeys: list[Journey], journey_id: str) -> Journey:
    for journey in journeys:
        if journey.journey_id == journey_id:
            return journey
    return None


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
    print("\n User Data")
    bot_data = context.bot_data
    print(bot_data)
    for user_id, data in bot_data.items():
        print("\n", user_id)
        print(data)

        start_stop_id = data["start_stop_id"]
        end_stop_id = data["end_stop_id"]
        tracked_journey_ids = data["tracked_journeys"]

        # get all journeys
        all_journeys = get_all_journeys(credentials.pass_id)

        for tracked_journey_id in tracked_journey_ids:
            tracked_journey = _get_journey_by_id(all_journeys, tracked_journey_id)
            if tracked_journey is None:
                # journey no longer exists
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"{tracked_journey_id} no longer exists",
                )
                context.bot_data[user_id]["tracked_journeys"].remove(tracked_journey_id)

                chat = await context.bot.get_chat(user_id)

                # print(chat.first_name)

                continue

            # get capacities
            print("Tracked journey found!")

    print("\n")
    #
    raise NotImplementedError
