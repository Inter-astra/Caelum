import html
import json
import os
from typing import List, Optional

from telegram import Update, ParseMode, TelegramError
from telegram.ext import CommandHandler, run_async, CallbackContext
from telegram.utils.helpers import mention_html

from tg_bot import (
    dispatcher,
    WHITELIST_USERS,
    SARDEGNA_USERS,
    SUPPORT_USERS,
    SUPER_ADMINS,
    SUDO_USERS,
    OWNER_ID,
)
from tg_bot.modules.helper_funcs.chat_status import whitelist_plus, dev_plus, sudo_plus
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.log_channel import gloggable

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "tg_bot/elevated_users.json")


def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        return "That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        return "This does not work that way."

    else:
        return None


def send_nations(update):
    message.reply_text(
        nations, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
    )


@whitelist_plus
def rlist(update: Update, context: CallbackContext):
    bot = context.bot
    true_sudo = list(set(SUDO_USERS))
    reply1 = "<b>Known Sudo Users :</b>\n"
    reply2 = "\n<b>Known Super Admins :</b>\n"
    reply3 = "\n<b>Known Support Users :</b>\n"
    reply4 = "\n<b>Known Sardegna Users :</b>\n"
    reply5 = "\n<b>Known Whitelisted Users :</b>\n"

    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply1 += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass

    for each_user in SUPER_ADMINS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply2 += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass

    for each_user in SUPPORT_USERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply3 += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass

    for each_user in SARDEGNA_USERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply4 += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass

    for each_user in WHITELIST_USERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply5 += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply1 + reply2 + reply3 + reply4 + reply5, parse_mode=ParseMode.HTML)


from tg_bot.modules.language import gs

RLIST_HANDLER = CommandHandler(["rlist", "rightlist"], rlist)

dispatcher.add_handler(RLIST_HANDLER)

__mod_name__ = "Nations"
__handlers__ = [
    RLIST_HANDLER,
]
