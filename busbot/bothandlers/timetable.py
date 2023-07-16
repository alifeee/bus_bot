"""/timetable"""
from telegram import *
from telegram.ext import *

from ..busapi import Credentials, get_all_journeys, get_journey_capacities
from ..stop import Stop
from ..journey import Journey

credentials = Credentials("credentials.json")

_TIMETABLE_MESSAGE = """
Here's the timetable for this week.
Start: {start}
End: {end}

{timetable}
"""

_TIMETABLE_ROW = """{time}: {journeytype} - {capacity} seats
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


async def _timetable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text("Getting timetable...")
    all_journeys = get_all_journeys(credentials.pass_id)

    if len(all_journeys) == 0:
        await message.edit_text(
            "Something went wrong... no journeys found. Try again? or ask Alfie"
        )
        return ConversationHandler.END

    start_stop_id = context.user_data["start_stop_id"]
    end_stop_id = context.user_data["end_stop_id"]
    if start_stop_id is None or end_stop_id is None:
        await message.edit_text("Start or end stop not set. Use /start.")
        return ConversationHandler.END

    for journey in all_journeys:
        if start_stop_id not in [s.stop_id for s in journey.stops]:
            continue
        if end_stop_id not in [s.stop_id for s in journey.stops]:
            continue

        if journey.type == "OUTBOUND":
            start_stop = _get_stop_by_id(journey.stops, start_stop_id)
            end_stop = _get_stop_by_id(journey.stops, end_stop_id)
        elif journey.type == "RETURN":
            start_stop = _get_stop_by_id(journey.stops, end_stop_id)
            end_stop = _get_stop_by_id(journey.stops, start_stop_id)

        journey.start_stop = start_stop
        journey.end_stop = end_stop

    capacities = get_journey_capacities(all_journeys)

    timetable = ""
    for journey in all_journeys:
        start_stop = journey.start_stop
        end_stop = journey.end_stop

        if journey.type == "OUTBOUND":
            time = start_stop.journey_stop_time
        elif journey.type == "RETURN":
            time = end_stop.journey_stop_time

        timetable += _TIMETABLE_ROW.format(
            time=time.strftime("%a %H:%M"),
            journeytype=journey.type,
            capacity=capacities[journey.journey_id],
        )

    start_stop_name = all_journeys[0].start_stop.name
    end_stop_name = all_journeys[0].end_stop.name
    await message.edit_text(
        _TIMETABLE_MESSAGE.format(
            start=start_stop_name, end=end_stop_name, timetable=timetable
        )
    )


timetable_handler = CommandHandler("timetable", _timetable)
