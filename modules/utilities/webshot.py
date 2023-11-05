from . import Client, BotContext, MessageEvent
from playwright.async_api import async_playwright
from secrets import token_hex
from urllib.parse import urlparse
from io import BytesIO


@Client.on_command("webshot")
async def webshot(ctx: BotContext[MessageEvent]):
    event = ctx.event.message
    try:
        url = ctx.event.message.message.split(maxsplit=1)[1]
    except IndexError:
        await event.reply_text("Provide a url to webshot")
        return
    parse = urlparse(url)
    if not (parse.netloc and parse.hostname):
        await event.reply_text("Invalid url provided.")
        return
    bt = await event.reply_text("Processing")
    async with async_playwright() as play:
        chrome = await play.chromium.launch()
        page = await chrome.new_page()
        await page.goto(url)
        img = BytesIO(await page.screenshot(full_page=True))
        img.name = "image.png"
    await event.reply_media(
        "Webshot.png", document=img, description=url, is_document=True,
        thumb=img
    )
    await bt.delete()
