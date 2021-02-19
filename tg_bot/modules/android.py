import rapidjson as json
from tg_bot import kp
from pyrogram import Client, filters


@kp.on_message(filters.command(["magisk"], prefixes=["/", "!", ","]))
async def magisk(client, message):

    url = 'https://raw.githubusercontent.com/topjohnwu/magisk_files/'
    releases = '**Latest Magisk Releases:**\n'
    variant = ['master/stable', 'master/beta', 'canary/canary']
    for variants in variant:
        fetch = get(url + variants + '.json')
        data = json.loads(fetch.content)
        if variants == "master/stable":
            name = "**Stable**"
            cc = 0
            branch = "master"
        elif variants == "master/beta":
            name = "**Beta**"
            cc = 0
            branch = "master"
        elif variants == "canary/canary":
            name = "**Canary**"
            cc = 1
            branch = "canary"

        if variants == "canary/canary":
            releases += f'{name}: [ZIP v{data["magisk"]["version"]}]({url}{branch}/{data["magisk"]["link"]}) | ' \
                        f'[APK v{data["app"]["version"]}]({url}{branch}/{data["app"]["link"]}) | '
        else:
            releases += f'{name}: [ZIP v{data["magisk"]["version"]}]({data["magisk"]["link"]}) | ' \
                        f'[APK v{data["app"]["version"]}]({data["app"]["link"]}) | '

        if cc == 1:
            releases += f'[Uninstaller]({url}{branch}/{data["uninstaller"]["link"]}) | ' \
                        f'[Changelog]({url}{branch}/notes.md)\n'
        else:
            releases += f'[Uninstaller]({data["uninstaller"]["link"]})\n'

    await update.reply_text(releases, disable_web_page_preview=True)

@kp.on_message(filters.command(["orangefox", "of", "fox", "ofox"]))
async def orangefox(c: Client, update: Update):

    chat_id = update.chat.id

    try:
        codename = update.command[1]
    except Exception:
        codename = ''

    if codename == '':
        reply_text = "**OrangeFox Recovery is currently avaible for:**"

        devices = _send_request('device/releases/stable')
        for device in devices:
            reply_text += f"\n • {device['fullname']} (`{device['codename']}`)"

        reply_text += "\n\nYou can get latest release by using `/orangefox (codename)`"
        await update.reply_text(reply_text)
        return

    device = _send_request(f'device/{codename}')
    if not device:
        reply_text = "Device is not found!"
        await update.reply_text(reply_text)
        return

    release = _send_request(f'device/{codename}/releases/stable/last')
    if not release:
        reply_text = "Release is not found!"
        await update.reply_text(reply_text)
        return

    reply_text = "**OrangeFox Recovery Project**\n"
    reply_text += "**📱 Device:** {fullname} (`{codename}`)\n".format(
        fullname=device['fullname'],
        codename=device['codename']
    )
    reply_text += "**🔺 Version:** `{}`\n".format(release['version'])
    reply_text += "**📅 Release date:** {}\n".format(release['date'])
    reply_text += "**✅ File MD5:** `{}`\n".format(release['md5'])

    if device['maintained'] == 3:
        status = "Not maintained"
        status = "Maintained"

    reply_text += "**👨‍🔬 Maintainer:** {name}, {status}\n".format(
        name=device['maintainer']['name'],
        status=status
    )

    btn = "Click here to Download"
    url = (release['url'])
    keyboard = [[InlineKeyboardButton(
        text=btn, url=url)]]
    await update.reply_text(reply_text,
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            disable_web_page_preview=True)
    return


def _send_request(endpoint):
    API_HOST = 'https://api.orangefox.download/v2'
    response = get(API_HOST + "/" + endpoint)
    if response.status_code == 404:
        return False

    return json.loads(response.text)