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
from busbot.bothandlers.error import error_handler

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
        store_data=PersistenceInput(user_data=True, bot_data=False),
    )
    loop = asyncio.new_event_loop()
    all_user_data = loop.run_until_complete(persistent_data.get_user_data())
    logger.info("Loaded user data:", all_user_data)
    loop.close()

    async def add_credentials_to_application(application: Application) -> None:
        application.bot_data["creds"] = Credentials("credentials.json")

    application = (
        Application.builder()
        .token(API_KEY)
        .persistence(persistent_data)
        .post_init(add_credentials_to_application)
        .build()
    )

    application.add_handler(start_handler)
    application.add_handler(timetable_handler)

    application.add_error_handler(error_handler)

    for user_id, user_data in all_user_data.items():
        continue

    application.run_polling()


if __name__ == "__main__":
    main()
