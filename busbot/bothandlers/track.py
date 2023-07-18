"""/track - command to enable/disable tracking of journeys"""

from telegram import *
from telegram.ext import *

from ..busapi import Credentials, get_all_journeys
from ..stop import Stop
from ..journey import Journey

credentials = Credentials("credentials.json")

_INITIAL_MESSAGE = """
Welcome to the tracking zone.

What do you want to do?
"""

_CHOICE_TRACK = "Track a journey"
_CHOICE_UNTRACK = "Untrack a journey"
_CHOICE_DONE = "Done"

_TRACK_JOURNEY_MESSAGE = """
Pick a journey to track and I'll send you a text whenever it has seats available.{day}{type}
"""

_JOURNEY_TRACKED_MESSAGE = """
Perfect! You're now tracking journey {journey_id}:
{journey_info}

...until it has been completed.

To disable this, use /track.
"""

_UNTRACK_JOURNEY_MESSAGE = """
Pick a journey to stop caring about:
"""

_NO_JOURNEYS_TRACKED_MESSAGE = """
You aren't tracking any journeys!
"""

_JOURNEY_UNTRACKED_MESSAGE = """
Okay! I'll no longer remind you about journey {journey_id}:
{journey_info}

To change this, use /track
"""

_DONE_MESSAGE = """
Super. Enjoy.
"""

(
    _CHOSEN_TRACK_OR_UNTRACK,
    _CHOSEN_JOURNEY_DAY,
    _CHOSEN_JOURNEY_TYPE,
    _CHOSEN_JOURNEY_TIME,
    _CHOSEN_JOURNEY_TO_UNTRACK,
) = range(5)


def ikb(text: str):
    return InlineKeyboardButton(text, callback_data=text)


MAIN_MENU_KEYBOARD = InlineKeyboardMarkup(
    [
        [ikb(_CHOICE_TRACK)],
        [ikb(_CHOICE_UNTRACK)],
        [ikb(_CHOICE_DONE)],
    ]
)


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


async def _track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        _INITIAL_MESSAGE,
        reply_markup=MAIN_MENU_KEYBOARD,
    )
    return _CHOSEN_TRACK_OR_UNTRACK


async def _track_journey_choose_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("Loading journeys...")

    all_journeys = get_all_journeys(credentials.pass_id)
    if len(all_journeys) == 0:
        await query.edit_message_text(
            """Something went wrong... no journeys found. Try again? or ask Alfie
            _track_journey_choose_day"""
        )
        return ConversationHandler.END
    start_stop_id = context.user_data.get("start_stop_id", None)
    end_stop_id = context.user_data.get("end_stop_id", None)
    if start_stop_id is None or end_stop_id is None:
        await query.edit_message_text("Start or end stop not set. Use /start.")
        return ConversationHandler.END
    relevant_journeys: list[Journey] = []
    for journey in all_journeys:
        if start_stop_id not in [s.stop_id for s in journey.stops]:
            continue
        if end_stop_id not in [s.stop_id for s in journey.stops]:
            continue
        relevant_journeys.append(journey)

        if journey.type == "OUTBOUND":
            start_stop = _get_stop_by_id(journey.stops, start_stop_id)
            end_stop = _get_stop_by_id(journey.stops, end_stop_id)
        elif journey.type == "RETURN":
            start_stop = _get_stop_by_id(journey.stops, end_stop_id)
            end_stop = _get_stop_by_id(journey.stops, start_stop_id)

        journey.start_stop = start_stop
        journey.end_stop = end_stop

    if len(relevant_journeys) == 0:
        await query.edit_message_text(
            "No journeys found between your two stops. Use /start or complain to Alfie"
        )
        return ConversationHandler.END

    journey_dict = {}
    for journey in relevant_journeys:
        journey_id = journey.journey_id
        journey_time = journey.start_stop.journey_stop_time.strftime("%H:%M")
        journey_type = journey.type
        journey_day = journey.day_and_date()
        if journey_day not in journey_dict:
            journey_dict[journey_day] = {}
        if journey_type not in journey_dict[journey_day]:
            journey_dict[journey_day][journey_type] = {}
        if journey_time not in journey_dict[journey_day][journey_type]:
            journey_dict[journey_day][journey_type][journey_time] = journey_id

    # {day: {type: {time: journey_id}}}
    context.user_data["journey_dict"] = journey_dict

    days_of_week_sorted = sorted(journey_dict.keys(), key=lambda x: x.split(" ")[-1])

    await query.edit_message_text(
        _TRACK_JOURNEY_MESSAGE.format(day="", type=""),
        reply_markup=InlineKeyboardMarkup([[ikb(day)] for day in days_of_week_sorted]),
    )
    return _CHOSEN_JOURNEY_DAY


async def _track_journey_choose_type(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    chosen_day = query.data
    context.user_data["chosen_day"] = chosen_day
    journey_dict = context.user_data["journey_dict"]

    journey_types = journey_dict[chosen_day].keys()
    await query.edit_message_text(
        _TRACK_JOURNEY_MESSAGE.format(day=f"\n\non {chosen_day}", type=""),
        reply_markup=InlineKeyboardMarkup([[ikb(t)] for t in journey_types]),
    )
    return _CHOSEN_JOURNEY_TYPE


async def _track_journey_choose_journey(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    chosen_day = context.user_data.get("chosen_day", None)
    chosen_type = query.data
    context.user_data["chosen_type"] = chosen_type
    journey_dict = context.user_data.get("journey_dict", {})

    print(f"chosen_day: {chosen_day}")
    print(f"chosen_type: {chosen_type}")
    print(f"journey_dict: {journey_dict}")

    journey_times = journey_dict[chosen_day][chosen_type]

    await query.edit_message_text(
        _TRACK_JOURNEY_MESSAGE.format(
            day=f"\n\non {chosen_day}", type=f"\n{chosen_type}"
        ),
        reply_markup=InlineKeyboardMarkup([[ikb(t)] for t in journey_times.keys()]),
    )
    return _CHOSEN_JOURNEY_TIME


async def _track_journey_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chosen_day = context.user_data.get("chosen_day", None)
    chosen_type = context.user_data.get("chosen_type", None)
    chosen_time = query.data
    journey_dict = context.user_data.get("journey_dict", {})

    chosen_journey_id = journey_dict[chosen_day][chosen_type][chosen_time]
    tracked_journeys = context.user_data.get("tracked_journeys", [])
    tracked_journeys.append(chosen_journey_id)
    context.user_data["tracked_journeys"] = tracked_journeys

    user_data = context.user_data
    user_data.pop("chosen_day", None)
    user_data.pop("chosen_type", None)
    user_data.pop("journey_dict", None)

    await query.edit_message_text(
        _JOURNEY_TRACKED_MESSAGE.format(
            journey_id=chosen_journey_id, journey_info="NO INFO YET"
        ),
        reply_markup=MAIN_MENU_KEYBOARD,
    )
    return _CHOSEN_TRACK_OR_UNTRACK


async def _untrack_journey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    tracked_journey_ids: list[str] = context.user_data.get("tracked_journeys", [])

    if len(tracked_journey_ids) == 0:
        try:
            await query.edit_message_text(
                _NO_JOURNEYS_TRACKED_MESSAGE, reply_markup=MAIN_MENU_KEYBOARD
            )
        finally:
            return _CHOSEN_TRACK_OR_UNTRACK

    await query.edit_message_text(
        _UNTRACK_JOURNEY_MESSAGE,
        reply_markup=InlineKeyboardMarkup(
            [[ikb(journey_id)] for journey_id in tracked_journey_ids]
        ),
    )
    return _CHOSEN_JOURNEY_TO_UNTRACK


async def _untrack_journey_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    journey_id = query.data
    tracked_journeys: list[str] = context.user_data.get("tracked_journeys", [])
    tracked_journeys.remove(journey_id)
    context.user_data["tracked_journeys"] = tracked_journeys

    await query.edit_message_text(
        _JOURNEY_UNTRACKED_MESSAGE.format(
            journey_id=journey_id, journey_info="did not actually do anything lol"
        ),
        reply_markup=MAIN_MENU_KEYBOARD,
    )
    return _CHOSEN_TRACK_OR_UNTRACK


async def _done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(_DONE_MESSAGE)
    return ConversationHandler.END


track_handler = ConversationHandler(
    entry_points=[CommandHandler("track", _track)],
    states={
        _CHOSEN_TRACK_OR_UNTRACK: [
            CallbackQueryHandler(_track_journey_choose_day, pattern=_CHOICE_TRACK),
            CallbackQueryHandler(_untrack_journey, pattern=_CHOICE_UNTRACK),
            CallbackQueryHandler(_done, pattern=_CHOICE_DONE),
        ],
        _CHOSEN_JOURNEY_DAY: [
            CallbackQueryHandler(_track_journey_choose_type, pattern=".*")
        ],
        _CHOSEN_JOURNEY_TYPE: [
            CallbackQueryHandler(_track_journey_choose_journey, pattern=".*")
        ],
        _CHOSEN_JOURNEY_TIME: [CallbackQueryHandler(_track_journey_id, pattern=".*")],
        _CHOSEN_JOURNEY_TO_UNTRACK: [
            CallbackQueryHandler(_untrack_journey_id, pattern=".*")
        ],
    },
    fallbacks=[],
)
