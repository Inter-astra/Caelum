import asyncio
from asyncio import sleep

from telethon import events
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

from tg_bot import telethn, OWNER_ID, SUDO_USERS, SUPER_ADMINS
from tg_bot.modules.language import gs

# =================== CONSTANT ===================

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)


UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

DELACCRM = [OWNER_ID] + SUDO_USERS + SUPER_ADMINS

# Check if user has admin rights
async def is_administrator(user_id: int, message):
    admin = False
    async for user in telethn.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id or user_id in DELACCRM:
            admin = True
            break
    return admin


@telethn.on(events.NewMessage(pattern=f"^[!/]delacc ?(.*)"))
async def zombies(event):
    """ For .zombies command, list all the deleted accounts in a chat. """

    con = event.pattern_match.group(1).lower()
    del_u = 0
    del_status = "No deleted accounts found, group is clean."

    if con != "clean":
        find_zombies = await event.respond("Searching for deleted accounts...")
        async for user in event.client.iter_participants(event.chat_id):

            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = f"Found **{del_u}** deleted accounts in this group.\
            \nClean them by using - `/delacc clean`"
        await find_zombies.edit(del_status)
        return

    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Well
    if not await is_administrator(user_id=event.from_id, message=event):
        await event.respond("You're not an admin!")
        return

    if not admin and not creator:
        await event.respond("I am not an admin here!")
        return

    cleaning_zombies = await event.respond("Removing deleted accounts...")
    del_u = 0
    del_a = 0

    async for user in event.client.iter_participants(event.chat_id):
        if user.deleted:
            try:
                await event.client(
                    EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                await cleaning_zombies.edit("I don't have ban rights in this group.")
                return
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1

    if del_u > 0:
        del_status = f"Cleaned `{del_u}` deleted accounts"

    if del_a > 0:
        del_status = f"Cleaned `{del_u}` deleted accounts \
        \n`{del_a}` Zombie admin accounts are not removed!"

    await cleaning_zombies.edit(del_status)

def get_help(chat):
    return gs(chat, "delacc_help")

__mod_name__ = "Deleted Accounts"