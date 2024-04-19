"""/whois"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

_WHOIS_MESSAGE = """
Whois!??!?
id: {id}
username: {username}
first_name: {first_name}
last_name: {last_name}
"""


async def _whois(update: Update, context: ContextTypes.DEFAULT_TYPE):

    input_mex = update.message.text
    input_args = input_mex.split("/whois ")[1]

    await update.message.reply_text(f"whois <{input_args}>?")

    try:
        chat = await context.bot.getChat(input_args)

        message = _WHOIS_MESSAGE.format(
            id=chat.id,
            username=chat.username,
            first_name=chat.first_name,
            last_name=chat.last_name,
        )

        await update.message.reply_text(message)
        await update.message.reply_text(f"{chat}")
    except Exception as ex:
        await update.message.reply_text(f"Failed... error:\n{ex}")


whois_handler = CommandHandler("whois", _whois)
