import html
from typing import List

from telegram import Update, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, CallbackContext
from telegram.utils.helpers import mention_html

from tg_bot import (
    dispatcher,
    log,
    SUDO_USERS,
    SARDEGNA_USERS,
    SUPPORT_USERS,
    OWNER_ID,
    WHITELIST_USERS,
)
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_can_ban,
)
from tg_bot.modules.helper_funcs.extraction import extract_user_and_text
from tg_bot.modules.helper_funcs.string_handling import extract_time
from tg_bot.modules.log_channel import loggable, gloggable
from tg_bot.modules.language import gs


@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def ban(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    log_message = ""
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Can't seem to find this person.")
            return log_message
        else:
            raise

    if user_id == context.bot.id:
        message.reply_text("I'm not gonna cut my own rope, are you crazy?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        if user_id == OWNER_ID:
            message.reply_text("I'd never ban my owner.")
            return log_message
        elif user_id in SUDO_USERS:
            message.reply_text("I can't ban a sudo user, try another one")
            return log_message
        elif user_id in SUPPORT_USERS:
            message.reply_text("Whaa tryna ban a gbanner? That won't happen!")
            return log_message
        elif user_id in SARDEGNA_USERS:
            message.reply_text("Hmm tryna ban a unbanner, nice try haha")
            return log_message
        elif user_id in WHITELIST_USERS:
            message.reply_text("You can't ban a whitelisted user, that's their purpose!")
            return log_message
        else:
            message.reply_text("Looks like this user is not punishable, so sad :(.")
            return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id)
        # context.bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        context.bot.sendMessage(
            chat.id, "I've cut the rope of {} 'till you decide to tie!".format(
                mention_html(member.user.id, member.user.first_name)
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("Banned", quote=False)
            return log
        else:
            log.warning(update)
            log.exception(
                "ERROR banning user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text(gs(chat, "not_bannable"))

    return ""


@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Can't seem to find this person.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("I'm not gonna cut my own rope, are you crazy?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I don't feel like it.")
        return log_message

    if not reason:
        message.reply_text("You haven't specified a time to cut the rope!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#TEMP BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.kick_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id, gs(chat, "succ_tbanned").format(
                mention_html(member.user.id, member.user.first_name)
            ))
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("I've cut this user's rope for {}").format(time_val)
            return log
        else:
            log.warning(update)
            log.exception(
                "ERROR cut rope of user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Well damn, I can't ban that user.")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def kick(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text(gs(chat, "cant_find"))
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text(gs(chat, "kick_myself"))
        return log_message

    if is_user_ban_protected(chat, user_id):
        message.reply_text(gs(chat, "not_bannable"))
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id, gs(chat, "succ_kick").format(
                mention_html(member.user.id, member.user.first_name))
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#CUTTHEROPE\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
        )
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

        return log


    else:
        message.reply_text(gs(chat, "cant_kick"))

    return log_message


@bot_admin
@can_restrict
def kickme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text(gs(chat, "you_admin"))
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text(gs(chat, "succ_kickme"))
    else:
        update.effective_message.reply_text(gs(chat, "fail_kickme"))


@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def unban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("Can't seem to find this person.")
            return log_message
        else:
            raise

    if user_id == bot.id:
        message.reply_text("How would I tie my own rope myself if I wasn't here...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("Isn't this person already here??")
        return log_message

    chat.unban_member(user_id)
    message.reply_text("Lemme tie this rope for you!")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    return log


@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(context: CallbackContext, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in SUDO_USERS or user.id not in SARDEGNA_USERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("Give a valid chat ID.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return
        else:
            raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("Aren't you already in the chat??")
        return

    chat.unban_member(user.id)
    message.reply_text("Done, your rope is tied back.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#TIEDTHEROPE\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    return log


def get_help(chat):
    return gs(chat, "bans_help")


BAN_HANDLER = CommandHandler("ban", ban, pass_args=True, run_async=True)
TEMPBAN_HANDLER = CommandHandler(
    ["tban", "tempban"], temp_ban, pass_args=True, run_async=True
)
PUNCH_HANDLER = CommandHandler(
    ["kick", "gtfo"], kick, pass_args=True, run_async=True
)
UNBAN_HANDLER = CommandHandler("unban", unban, pass_args=True, run_async=True)
ROAR_HANDLER = CommandHandler(
    ["roar", "selfunban"], selfunban, pass_args=True, run_async=True
)
PUNCHME_HANDLER = DisableAbleCommandHandler(
    ["kickme"], kickme, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(PUNCH_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(PUNCHME_HANDLER)

__mod_name__ = "Bans"
__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    PUNCH_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    PUNCHME_HANDLER,
]
