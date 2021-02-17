import logging
import os
import sys
import time
import spamwatch
import telegram.ext as tg
from telethon import TelegramClient
from pyrogram import Client, errors
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, ChannelInvalid
from pyrogram.types import Chat, User
from configparser import ConfigParser
from rich.logging import RichHandler
StartTime = time.time()

# enable logging
FORMAT = "%(message)s"
logging.basicConfig(handlers=[RichHandler()], level=logging.INFO, format=FORMAT, datefmt="[%X]")
log = logging.getLogger("rich")


log.info("Calum is now ON. | Licensed under GPLv3.")

log.info("Project maintained by;")
log.info("github.com/Dank-del (t.me/dank_as_fuck) and github.com/Stacia-Sama (t.me/Inter_Astra)")
log.info("Read README.md please!")
# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    log.error("You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting.")
    quit(1)

parser = ConfigParser()
parser.read("config.ini")
Caelconfig = parser["Caelconfig"]


OWNER_ID = Caelconfig.getint("OWNER_ID")
OWNER_USERNAME = Caelconfig.get("OWNER_USERNAME")
SCHAT = Caelconfig.get("SUPPORT_CHAT")
APP_ID = Caelconfig.getint("APP_ID")
API_HASH = Caelconfig.get("API_HASH")
WEBHOOK = Caelconfig.getboolean("WEBHOOK")
URL = Caelconfig.get("URL")
CERT_PATH = Caelconfig.get("CERT_PATH")
PORT = Caelconfig.getint("PORT")
INFOPIC = Caelconfig.getboolean("INFOPIC")
DEL_CMDS = Caelconfig.getboolean("DEL_CMDS")
STRICT_GBAN = Caelconfig.getboolean("STRICT_GBAN")
ALLOW_EXCL = Caelconfig.getboolean("ALLOW_EXCL")
CUSTOM_CMD = Caelconfig.get("CUSTOM_CMD")
BAN_STICKER = Caelconfig.get("BAN_STICKER")
WORKERS = Caelconfig.getint("WORKERS")
TOKEN = Caelconfig.get("TOKEN")
DB_URI = Caelconfig.get("SQLALCHEMY_DATABASE_URI")
LOAD = Caelconfig.get("LOAD").split()
LOAD = list(map(str, LOAD))
MESSAGE_DUMP = Caelconfig.getfloat("MESSAGE_DUMP")
GBAN_LOGS = Caelconfig.getfloat("GBAN_LOGS")
NO_LOAD = Caelconfig.get("NO_LOAD").split()
NO_LOAD = list(map(str, NO_LOAD))
SUDO_USERS = Caelconfig.get("SUDO_USERS").split()
SUDO_USERS = list(map(int, SUDO_USERS))
SUPER_ADMINS = Caelconfig.get("SUPER_ADMINS").split()
SUPER_ADMINS = list(map(int, SUPER_ADMINS))
SUPPORT_USERS = Caelconfig.get("SUPPORT_USERS").split()
SUPPORT_USERS = list(map(int, SUPPORT_USERS))
SARDEGNA_USERS = Caelconfig.get("SARDEGNA_USERS").split()
SARDEGNA_USERS = list(map(int, SARDEGNA_USERS))
WHITELIST_USERS = Caelconfig.get("WHITELIST_USERS").split()
WHITELIST_USERS = list(map(int, WHITELIST_USERS))
SPAMMERS = Caelconfig.get("SPAMMERS").split()
SPAMMERS = list(map(int, SPAMMERS))
spamwatch_api = Caelconfig.get("spamwatch_api")
CASH_API_KEY = Caelconfig.get("CASH_API_KEY")
TIME_API_KEY = Caelconfig.get("TIME_API_KEY")
WALL_API = Caelconfig.get("WALL_API")
LASTFM_API_KEY = Caelconfig.get("LASTFM_API_KEY")


SUDO_USERS.append(OWNER_ID)

# SpamWatch
if spamwatch_api is None:
    sw = None
    log.warning("SpamWatch API key is missing! Check your config.ini")
else:
    try:
        sw = spamwatch.Client(spamwatch_api)
    except:
        sw = None
        log.warning("Can't connect to SpamWatch!")

updater = tg.Updater(TOKEN, workers=WORKERS)
telethn = TelegramClient("Caelum", APP_ID, API_HASH)
dispatcher = updater.dispatcher

kp = Client("CaelumPyro", api_id=APP_ID, api_hash=API_HASH, bot_token=TOKEN)
apps = []
apps.append(kp)


async def get_entity(client, entity):
    entity_client = client
    if not isinstance(entity, Chat):
        try:
            entity = int(entity)
        except ValueError:
            pass
        except TypeError:
            entity = entity.id
        try:
            entity = await client.get_chat(entity)
        except (PeerIdInvalid, ChannelInvalid):
            for kp in apps:
                if kp != client:
                    try:
                        entity = await kp.get_chat(entity)
                    except (PeerIdInvalid, ChannelInvalid):
                        pass
                    else:
                        entity_client = kp
                        break
            else:
                entity = await kp.get_chat(entity)
                entity_client = kp
    return entity, entity_client


SUDO_USERS = list(SUDO_USERS)
SUPER_ADMINS = list(SUPER_ADMINS)
WHITELIST_USERS = list(WHITELIST_USERS)
SUPPORT_USERS = list(SUPPORT_USERS)
SARDEGNA_USERS = list(SARDEGNA_USERS)
SPAMMERS = list(SPAMMERS)

# Load at end to ensure all prev variables have been set
from tg_bot.modules.helper_funcs.handlers import CustomCommandHandler

if CUSTOM_CMD and len(CUSTOM_CMD) >= 1:
    tg.CommandHandler = CustomCommandHandler


def spamfilters(text, user_id, chat_id):
    # print("{} | {} | {}".format(text, user_id, chat_id))
    if int(user_id) in SPAMMERS:
        print("This user is a spammer!")
        return True
    else:
        return False
