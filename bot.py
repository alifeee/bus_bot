"""The bot!"""

import os
import logging
import asyncio
import sys

from dotenv import load_dotenv
from telegram import *
from telegram.ext import *

from busbot.busapi import Credentials
from busbot.bothandlers.start import start_handler
from busbot.bothandlers.timetable import timetable_handler
from busbot.bothandlers.track import track_handler
from busbot.bothandlers.whois import whois_handler
from busbot.bothandlers.error import error_handler
from busbot.reminderer import initialise_job

# I don't use this but you can use it to set commands with @botfather with /setcommands
_ = """
start - set up
timetable - get timetable
"""

load_dotenv()
try:
    API_KEY = os.environ["TELEGRAM_BOT_ACCESS_TOKEN"]
except KeyError as error:
    raise ValueError(
        "TELEGRAM_BOT_ACCESS_TOKEN environment variable not set"
    ) from error

if len(sys.argv) > 1 and sys.argv[1] == "debug":
    RUN_ON_STARTUP = True
else:
    RUN_ON_STARTUP = False

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot!"""
    persistent_data = PicklePersistence(
        filepath="bot_data.pickle",
        store_data=PersistenceInput(user_data=False, bot_data=True),
    )

    application = (
        Application.builder().token(API_KEY).persistence(persistent_data).build()
    )

    application.add_handler(start_handler)
    application.add_handler(timetable_handler)
    application.add_handler(track_handler)
    application.add_handler(whois_handler)

    application.add_error_handler(error_handler)

    initialise_job(application.job_queue)

    application.run_polling()


if __name__ == "__main__":
    main()
