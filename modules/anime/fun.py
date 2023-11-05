from . import *
from io import BytesIO

@Bot.on_command("pat")
async def patSomeone(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    replied = await m.get_replied_message()
    if replied:
        title = f"{m.user.name} pats {replied.user.name}"
    else:
        title = f"{ctx.user.name} pats {m.user.name}"
    try:
        data = requests.get("https://nekos.life/api/v2/img/pat").json()
    except Exception as er:
        LOG.exception(er)
        return
    img = BytesIO(requests.get(data['url']).content)
    img.name = "image.gif"
    await m.reply_text(
        title,
        document=img,
        thumb=img,
    )

@Bot.on_command("slap")
async def slapSomeone(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    replied = await m.get_replied_message()
    if replied:
        title = f"{m.user.name} slaps {replied.user.name}"
    else:
        title = f"{ctx.user.name} slaps {m.user.name}"
    try:
        data = requests.get("https://nekos.life/api/v2/img/slap").json()
    except Exception as er:
        LOG.exception(er)
        return
    img = BytesIO(requests.get(data['url']).content)
    img.name = "image.gif"
    await m.reply_text(
        title,
        document=img,
        thumb=img,
    )