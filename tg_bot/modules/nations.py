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

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "tg_bot/elevated_users.json")


def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        reply = "That...is a chat! baka ka omae?"

    elif user_id == bot.id:
        reply = "Do I look like a user? "

    elif user_id == OWNER_ID:
        reply = "You are my owner, I'm not gonna do this."

    else:
        reply = None
    return reply

@dev_plus
def addsudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        message.reply_text("This member is already a Sudo user")
        return ""

    if user_id in SUPPORT_USERS:
        rt += "Requested Starlight to promote a Support user to Sudo."
        data["supports"].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "Requested Starlight to promote a Whitelist user to Sudo."
        data["whitelists"].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    data["sudos"].append(user_id)
    SUDO_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt
        + "\nSuccessfully promoted {} to Sudo!".format(
            user_member.first_name
        )
    )


@dev_plus
def addsuper(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in SUPER_ADMINS:
        message.reply_text("This member is already a super admin")
        return ""

    if user_id in SUPPORT_USERS:
        rt += "Requested Starlight to promote a Support user to Sudo."
        data["supports"].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "Requested Starlight to promote a Whitelist user to Sudo."
        data["whitelists"].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    data["supers"].append(user_id)
    SUPER_ADMINS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt
        + "\nSuccessfully promoted {} to Super Admin!".format(
            user_member.first_name
        )
    )



@sudo_plus
def addsupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "Requested Starlight to demote this Sudo to support"
        data["sudos"].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        message.reply_text("This user is already a Support user.")
        return ""

    if user_id in WHITELIST_USERS:
        rt += "Requested Starlight to promote this Whitelist user to Demon"
        data["whitelists"].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    data["supports"].append(user_id)
    SUPPORT_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\n{user_member.first_name} was added as a Support user!"
    )



@sudo_plus
def addwhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "This member is a Sudo user, demoting to Whitelisted user."
        data["sudos"].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        rt += "This user is already a Support user, demoting to Whitelisted user."
        data["supports"].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        message.reply_text("This user is already a Whitelist user.")
        return ""

    data["whitelists"].append(user_id)
    WHITELIST_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Whitelist user!"
    )



@sudo_plus
def addsardegna(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "This member is a Sudo user, Demoting to Sardegna."
        data["sudos"].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        rt += "This user is already a Support user, Demoting to Sardegna."
        data["supports"].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "This user is already a Whitelist user, Demoting to Sardegna."
        data["whitelists"].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    if user_id in SARDEGNA_USERS:
        message.reply_text("This user is already a Sardegna.")
        return ""

    data["sardegnas"].append(user_id)
    SARDEGNA_USERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Sardegna Nation!")



@dev_plus
def removesudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        message.reply_text("Requested Starlight to demote this user to Civilian")
        SUDO_USERS.remove(user_id)
        data["sudos"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

    else:
        message.reply_text("This user is not a Sudo user!")
        return ""



@dev_plus
def removesuper(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        message.reply_text("Requested Starlight to demote this user to Civilian")
        SUPER_ADMINS.remove(user_id)
        data["supers"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

    else:
        message.reply_text("This user is not a Super Amin!")
        return ""




@sudo_plus
def removesupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in SUPPORT_USERS:
        message.reply_text("Requested Starlight to demote this user to Civilian")
        SUPPORT_USERS.remove(user_id)
        data["supports"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

    else:
        message.reply_text("This user is not a Support user!")
        return ""



@sudo_plus
def removewhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in WHITELIST_USERS:
        message.reply_text("Demoting to normal user")
        WHITELIST_USERS.remove(user_id)
        data["whitelists"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

    else:
        message.reply_text("This user is not a Whitelist user!")
        return ""



@sudo_plus
def removesardegna(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in SARDEGNA_USERS:
        message.reply_text("Demoting to normal user")
        SARDEGNA_USERS.remove(user_id)
        data["sardegnas"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

    else:
        message.reply_text("This user is not a Sardegna user!")
        return ""


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


RLIST_HANDLER = CommandHandler(["rlist", "rightlist"], rlist)

SUDO_HANDLER = CommandHandler("addsudo", addsudo)
SA_HANDLER = CommandHandler("addsa", addsuper)
SUPPORT_HANDLER = CommandHandler("addsupport", addsupport)
SD_HANDLER = CommandHandler("addsar", addsardegna)
WHITELIST_HANDLER = CommandHandler("addwt", addwhitelist)
UNSUDO_HANDLER = CommandHandler("removesudo", removesudo)
UNSA_HANDLER = CommandHandler("removesa", removesuper)
UNSUPPORT_HANDLER = CommandHandler("removesupport", removesupport)
UNSD_HANDLER = CommandHandler("removesar", removesardegna)
UNWHITELIST_HANDLER = CommandHandler("removewt", removewhitelist)

dispatcher.add_handler(RLIST_HANDLER)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SA_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(SD_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSA_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNSD_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)

__handlers__ = [
    RLIST_HANDLER,
    SUDO_HANDLER,
    SA_HANDLER,
    SUPPORT_HANDLER,
    SD_HANDLER,
    WHITELIST_HANDLER,
    UNSUDO_HANDLER,
    UNSA_HANDLER,
    UNSUPPORT_HANDLER,
    UNSD_HANDLER,
    UNWHITELIST_HANDLER,
]
