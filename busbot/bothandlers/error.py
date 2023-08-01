"""Error handler: sends "admin" a message with the error and the update that caused it."""
import os
import logging
import traceback
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

_ERROR_MESSAGE = """
Error!

User: {user}

Chat: {chat}

Update: {update}

Job: {job}

Error: {error}

Trace: {trace}
"""


async def error_handler(
    update: Update | None, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends traceback to admin."""
    bot = context.bot
    try:
        admin_id = os.environ["ADMIN_USER_ID"]
    except KeyError as error:
        raise ValueError("ADMIN_USER_ID environment variable not set.") from error

    try:
        tbs = traceback.format_tb(context.error.__traceback__)
        err_traceback = "".join(tbs)
    except AttributeError:
        err_traceback = ""

    if update is not None:
        await bot.send_message(
            chat_id=admin_id,
            text=_ERROR_MESSAGE.format(
                user=update.effective_user,
                chat=update.effective_chat,
                update=update,
                job="N/A",
                error=context.error,
                trace=err_traceback,
            ),
        )
    elif context.job is not None:
        await bot.send_message(
            chat_id=admin_id,
            text=_ERROR_MESSAGE.format(
                user="N/A",
                chat="N/A",
                update="N/A",
                job=context.job.name,
                error=context.error,
                trace=err_traceback,
            ),
        )

    print(context)
    logger = logging.getLogger(__name__)
    try:
        if context.error is not None:
            logger.error("Update %s caused error %s", update.update_id, context.error)
            logger.error(context.error)
    except AttributeError:
        logger.error("Update caused error %s", context.error)
    # raise context.error
