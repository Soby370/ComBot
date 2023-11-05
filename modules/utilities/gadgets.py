import re, os
import requests
from io import BytesIO
from bs4 import BeautifulSoup as bs
from . import *


@Client.on_command("gadget")
async def get_gadget(ctx: BotContext[MessageEvent]):
    event = ctx.event.message
    try:
        mat = ctx.event.message.message.split(maxsplit=1)[1]
    except IndexError:
        await event.reply_text("Please Give a gadget name to look for.")
        return
    query = mat.replace(" ", "%20")
    jwala = f"https://gadgets.ndtv.com/search?searchtext={query}"
    c = requests.get(jwala).content
    b = bs(c, "html.parser", from_encoding="utf-8")
    co = b.find_all("div", "rvw-imgbox")
    if not co:
        return await event.reply_text("No Results Found!")
    bt = await event.reply_text("Processing")
    out = "*📱 Mobile / Gadgets Search*\n\n"
    li = co[0].find("a")
    imu, title = None, li.find("img")["title"]
    cont = requests.get(li["href"]).content
    nu = bs(cont, "html.parser", from_encoding="utf-8")
    req = nu.find_all("div", "_pdsd")
    imu = nu.find_all(
        "img", src=re.compile("https://i.gadgets360cdn.com/products/large/")
    )
    if imu:
        imu = imu[0]["src"].split("?")[0]  # + "?downsize=*:420&output-quality=80"
    out += f"☑️ *{title}* {li['href']}\n\n"
    for fp in req:
        ty = fp.findNext()
        out += f"- *{ty.text}* : {ty.findNext().text}\n"
    out += "_"
    if imu:
        file = BytesIO(requests.get(imu).content)
        file.name = "gadget.png"
        await event.reply_media(out, document=file, description=out, thumb=file)
    else:
        await event.reply_text(out)
    await bt.delete()