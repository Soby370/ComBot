from . import *
from io import BytesIO


@Bot.on_command("waifu")
async def patSomeone(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    try:
        data = requests.get("https://nekos.life/api/v2/img/waifu").json()
    except Exception as er:
        LOG.exception(er)
        return
    img = BytesIO(requests.get(data["url"]).content)
    img.name = "image.png"
    await m.reply_text(message="*Here is your Waifu!*", document=img, description="Waifu.png",
                       thumb=img)
