"""/start"""
from telegram import *
from telegram.ext import *

_START_MESSAGE = "Woohoo!"


async def _start(update: Update, _):
    message = await update.message.reply_text(
        "What's your start stop?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("stop 1", callback_data="stop 1")],
                [InlineKeyboardButton("stop 2", callback_data="stop 2")],
            ]
        ),
    )


start_handler = CommandHandler("start", _start)
