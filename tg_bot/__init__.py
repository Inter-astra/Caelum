import logging
import os
import sys, json
import time
import spamwatch
import telegram.ext as tg
from telethon import TelegramClient
from telethon.sessions import MemorySession
from pyrogram import Client, errors
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, ChannelInvalid
from pyrogram.types import Chat, User
from configparser import ConfigParser
from rich.logging import RichHandler
from ptbcontrib.postgres_persistence import PostgresPersistence


StartTime = time.time()

def get_user_list(__init__, key):
    with open("{}/tg_bot/{}".format(os.getcwd(), __init__), "r") as json_file:
        return json.load(json_file)[key]

# enable logging
FORMAT = "%(message)s"
logging.basicConfig(handlers=[RichHandler()], level=logging.INFO, format=FORMAT, datefmt="[%X]")
logging.getLogger("pyrogram").setLevel(logging.WARNING)
log = logging.getLogger("rich")


log.info("[Caelum] Calum is now ON. | Licensed under GPLv3.")

log.info("[Caelum] Project maintained by;")
log.info("[Caelum] github.com/Dank-del (t.me/dank_as_fuck) and github.com/Stella-Lucem (t.me/Stella-Lucem)")
log.info("[Caelum] Read README.md please!")
# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    log.error("[Caelum] You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting.")
    quit(1)

parser = ConfigParser()
parser.read("config.ini")
Caelconfig = parser["Caelconfig"]


OWNER_ID = Caelconfig.getint("OWNER_ID")
OWNER_USERNAME = Caelconfig.get("OWNER_USERNAME")
SCHAT = Caelconfig.get("SUPPORT_CHAT")
APP_ID = Caelconfig.getint("APP_ID")
API_HASH = Caelconfig.get("API_HASH")
WEBHOOK = Caelconfig.getboolean("WEBHOOK", False)
URL = Caelconfig.get("URL", None)
CERT_PATH = Caelconfig.get("CERT_PATH", None)
PORT = Caelconfig.getint("PORT", None)
INFOPIC = Caelconfig.getboolean("INFOPIC", False)
DEL_CMDS = Caelconfig.getboolean("DEL_CMDS", False)
STRICT_GBAN = Caelconfig.getboolean("STRICT_GBAN", False)
ALLOW_EXCL = Caelconfig.getboolean("ALLOW_EXCL", False)
CUSTOM_CMD = Caelconfig.get("CUSTOM_CMD", False).split()
BAN_STICKER = Caelconfig.get("BAN_STICKER", None)
TOKEN = Caelconfig.get("TOKEN")
DB_URI = Caelconfig.get("SQLALCHEMY_DATABASE_URI")
LOAD = Caelconfig.get("LOAD").split()
LOAD = list(map(str, LOAD))
MESSAGE_DUMP = Caelconfig.getfloat("MESSAGE_DUMP")
GBAN_LOGS = Caelconfig.getfloat("GBAN_LOGS")
NO_LOAD = Caelconfig.get("NO_LOAD").split()
NO_LOAD = list(map(str, NO_LOAD))
SUDO_USERS = get_user_list("elevated_users.json", "sudos")
SUPER_ADMINS = get_user_list("elevated_users.json", "supers")
SUPPORT_USERS = get_user_list("elevated_users.json", "supports")
SARDEGNA_USERS = get_user_list("elevated_users.json", "sardegnas")
WHITELIST_USERS = get_user_list("elevated_users.json", "whitelists")
SPAMMERS = get_user_list("elevated_users.json", "spammers")
spamwatch_api = Caelconfig.get("spamwatch_api")
CASH_API_KEY = Caelconfig.get("CASH_API_KEY")
TIME_API_KEY = Caelconfig.get("TIME_API_KEY")
WALL_API = Caelconfig.get("WALL_API")
LASTFM_API_KEY = Caelconfig.get("LASTFM_API_KEY")
BL_CHATS = Caelconfig.get("BL_Chats").split()
BL_CHATS = list(map(int, BL_CHATS))

try:
    CF_API_KEY = Caelconfig.get("CF_API_KEY")
    log.info("AI antispam powered by Intellivoid.")
except:
    log.info("No Coffeehouse API key provided.")
    CF_API_KEY = None


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


from tg_bot.modules.sql import SESSION


updater = tg.Updater(TOKEN, workers=min(32, os.cpu_count() + 4), request_kwargs={"read_timeout": 10, "connect_timeout": 10}, persistence=PostgresPersistence(SESSION))
telethn = TelegramClient(MemorySession(), APP_ID, API_HASH)
dispatcher = updater.dispatcher

kp = Client(":memory:", api_id=APP_ID, api_hash=API_HASH, bot_token=TOKEN, workers=min(32, os.cpu_count() + 4))
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
