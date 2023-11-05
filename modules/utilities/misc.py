import requests
from . import *


@Client.on_command("ipinfo")
async def ipInfoCmd(ctx: BotContext[MessageEvent]):
    event = ctx.event.message
    try:
        ip = event.message.split(maxsplit=1)[1]
    except IndexError:
        await event.reply_text("Provide a IP address to get info.")
        return
    det = requests.get(f"https://ipinfo.io/geo/{ip}").json()
    try:
        ip = det["ip"]
        city = det["city"]
        region = det["region"]
        country = det["country"]
        cord = det["loc"]
        try:
            zipc = det["postal"]
        except KeyError:
            zipc = "None"
        tz = det["timezone"]
        await event.reply_text(
            """
*IP Details Fetched.*

*IP:* {}
*City:* {}
*Region:* {}
*Country:* {}
*Co-ordinates:* {}
*Postal Code:* {}
*Time Zone:* {}
""".format(
                ip,
                city,
                region,
                country,
                cord,
                zipc,
                tz,
            ),
        )
    except BaseException:
        err = det["error"]["title"]
        msg = det["error"]["message"]
        await event.reply_text(f"ERROR:\n{err}\n{msg}")