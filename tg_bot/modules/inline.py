import html
from platform import python_version
from uuid import uuid4

from spamprotection.errors import HostDownError
from spamprotection.sync import SPBClient
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram import __version__
from telegram.error import BadRequest
from telegram.ext import InlineQueryHandler, CallbackContext
from telegram.utils.helpers import mention_html
from tg_bot.modules.helper_funcs.misc import article
import tg_bot.modules.sql.users_sql as sql
from tg_bot import (
    dispatcher,
    OWNER_ID,
    SUDO_USERS,
    SUPER_ADMINS,
    SUPPORT_USERS,
    SARDEGNA_USERS,
    WHITELIST_USERS,
    sw, log
)

client = SPBClient()


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        text = text.replace(prefix, "", 1)
    return text

def inlinequery(update: Update, _) -> None:
    """
    Main InlineQueryHandler callback.
    """
    query = update.inline_query.query
    user = update.effective_user

    results: List = []
    inline_help_dicts = [
        {
            "title": "User info on Caelum",
            "description": "Look up a person in Caelum database",
            "message_text": "Click the button below to look up a person in Caelum database using their Telegram ID",
            "thumb_urL": "https://telegra.ph/file/c1cbf81674a6ebd44fde0.jpg",
            "keyboard": ".info ",
        },
    #    {
    #        "title": "About",
    #        "description": "Know about Caelum",
    #        "message_text": "Click the button below to get to know about Caelum.",
    #        "thumb_urL": "https://telegra.ph/file/c1cbf81674a6ebd44fde0.jpg",
    #        "keyboard": ".about ",
    #    },
    ]

    inline_funcs = {
        ".info": inlineinfo,
    #    ".about": about,
    }

    if (f := query.split(" ", 1)[0]) in inline_funcs:
        inline_funcs[f](remove_prefix(query, f).strip(), update, user)
    else:
        for ihelp in inline_help_dicts:
            results.append(
                article(
                    title=ihelp["title"],
                    description=ihelp["description"],
                    message_text=ihelp["message_text"],
                    thumb_url=ihelp["thumb_urL"],
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Click Here",
                                    switch_inline_query_current_chat=ihelp[
                                        "keyboard"
                                    ],
                                )
                            ]
                        ]
                    ),
                )
            )

        update.inline_query.answer(results, cache_time=5)

def inlineinfo(query: str, update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    bot = context.bot
    query = update.inline_query.query
    log.info(query)
    user_id = update.effective_user.id
    try:
        search = query.split(" ", 1)[1]
    except IndexError:
        search = user_id

    try:
        user = bot.get_chat(int(search))
    except BadRequest:
        user = bot.get_chat(user_id)

    chat = update.effective_chat
    sql.update_user(user.id, user.username)

    text = (
        f"<b>User Info:</b>\n"
        f"ID: <code>{user.id}</code>\n"
        f"First Name: {html.escape(user.first_name)}"
    )

    if user.last_name:
        text += f"\nLast Name: {html.escape(user.last_name)}"

    if user.username:
        text += f"\nUsername: @{html.escape(user.username)}"

    text += f"\nPermanent user link: {mention_html(user.id, 'link')}"

    try:
        spamwtc = sw.get_ban(int(user.id))
        if spamwtc:
            text += "\n\n<b>This person is banned in Spamwatch!</b>"
            text += f"\nReason: <pre>{spamwtc.reason}</pre>"
            text += "\nAppeal at @SpamWatchSupport"

    except:
        pass  # don't crash if api is down somehow...

    try:
        status = client.raw_output(int(user.id))
        sp = status["results"]["spam_prediction"]["spam_prediction"]
        blc = status["results"]["attributes"]["is_blacklisted"]
        blcres = status["results"]["attributes"]["blacklist_reason"]

        if blc:
             text += f"\n\n<b>Spam Protection Stats:</b>\n"
             text += f"<b>Banned with reason:</b> <code>{blcres}</code>\n"
        if sp:
            text += f"\n\n<b>Spam Protection Stats:</b>\n"
            text += f"<b>Spam Prediction:</b> <code>{sp}</code>\n"

    except HostDownError:
        pass

    if user_id == 777000:
        text += f"\nThis is Telegram. It's everywhere or we'are in it, idk which one"
    elif user_id == 1087968824:
        text += f"\nThis is anonymous, used in chats to show someone as group or to hide user"
    elif user_id == dispatcher.bot.id:
        text += f"\nIs it possible to be everywhere I'm in? Oh, ahaha it's is me"

    if user.id == OWNER_ID:
        text += f"\nThis person is my owner."
    elif user.id in SUDO_USERS:
        text += f"\nThis user is a sudo."
    elif user.id in SUPER_ADMINS:
        text += f"\nThis user is a super admin."
    elif user.id in SUPPORT_USERS:
        text += f"\nThis user is a support."
    elif user.id in SARDEGNA_USERS:
        text += f"\nThis user is a sardegna."
    elif user.id in WHITELIST_USERS:
        text += f"\nThis user is whitelisted."

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title=f"User info of {html.escape(user.first_name)}",
            input_message_content=InputTextMessageContent(text, parse_mode=ParseMode.HTML,
                                                          disable_web_page_preview=True),
        ),
    ]

    update.inline_query.answer(results, cache_time=5)

def about(query: str, update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query
    user_id = update.effective_user.id
    user = context.bot.get_chat(user_id)
    sql.update_user(user.id, user.username)
    about_text = f"""
    Caelum (@{context.bot.username})
    Maintained by [Dank-del](t.me/dank_as_fuck) and [Stella](tg://user?id=1659080755)
    Built with ❤️ using python-telegram-bot v{str(__version__)}
    Running on Python {python_version()}
    """
    results: list = []
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Support",
                    url=f"https://t.me/CaelumSupport",
                ),
                InlineKeyboardButton(
                    text="Channel",
                    url=f"https://t.me/CaelumNews",
                ),

            ],
            [
                InlineKeyboardButton(
                    text="GitHub",
                    url="https://github.com/Stella-Lucem/Caelum",
                ),
            ],
        ])

    results.append(

        InlineQueryResultArticle
            (
            id=str(uuid4()),
            title=f"About Caelum (@{context.bot.username})",
            input_message_content=InputTextMessageContent(about_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True),
            reply_markup=kb
            )
       )
    update.inline_query.answer(results)


dispatcher.add_handler(InlineQueryHandler(inlinequery))