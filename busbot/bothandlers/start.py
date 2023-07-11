"""/start"""
from telegram import *
from telegram.ext import *

from ..busapi import Credentials, get_all_journeys, get_all_stops_from_journeys
from ..stop import Stop

credentials = Credentials("credentials.json")

_START_MESSAGE = """
Hi!

Choose your start and end stops and I can filter out journeys to only show ones between those.

{state}
"""

_END_MESSAGE = """
Nice!

I'll now only show journeys between {start} and {end}.

Use /start to change this.

Check /timetable for the capacities of all upcoming buses.
"""


_CHOOSING_END_STOP, _CONFIRMING_END_STOP = range(2)


async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_journeys = get_all_journeys(credentials.pass_id)
    all_stops = get_all_stops_from_journeys(all_journeys)
    context.bot_data["all_stops"] = all_stops

    await update.message.reply_text(
        _START_MESSAGE.format(state="What's your start stop?"),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(stop.name, callback_data=stop.stop_id)]
                for stop in all_stops
            ]
        ),
    )
    return _CHOOSING_END_STOP


async def _choose_end_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_stops: list[Stop] = context.bot_data["all_stops"]
    query = update.callback_query
    await query.answer()

    start_stop_id = query.data
    context.user_data["start_stop_id"] = start_stop_id

    # find the stop
    for stop in all_stops:
        if stop.stop_id == start_stop_id:
            break
    else:
        raise ValueError(f"Stop {start_stop_id} not found")

    await query.edit_message_text(
        _START_MESSAGE.format(
            state=f"Your start stop is: {stop.name}\nNow for the end stop:"
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(stop.name, callback_data=stop.stop_id)]
                for stop in all_stops
            ]
        ),
    )
    return _CONFIRMING_END_STOP


async def _confirm_choices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_stops: list[Stop] = context.bot_data["all_stops"]
    query = update.callback_query
    await query.answer()

    end_stop_id = query.data
    context.user_data["end_stop_id"] = end_stop_id
    start_stop_id = context.user_data["start_stop_id"]

    for end_stop in all_stops:
        if end_stop.stop_id == end_stop_id:
            break
    else:
        raise ValueError(f"Stop {end_stop_id} not found")

    for start_stop in all_stops:
        if start_stop.stop_id == start_stop_id:
            break
    else:
        raise ValueError(f"Stop {start_stop_id} not found")

    await query.edit_message_text(
        _START_MESSAGE.format(
            state=f"Your start stop is: {start_stop.name}\nYour end stop is: {end_stop.name}\n\nUse /start again to change this :)"
        )
    )
    return ConversationHandler.END


start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", _start)],
    states={
        _CHOOSING_END_STOP: [CallbackQueryHandler(_choose_end_stop, pattern="^.*$")],
        _CONFIRMING_END_STOP: [CallbackQueryHandler(_confirm_choices, pattern="^.*$")],
    },
    fallbacks=[],
)
