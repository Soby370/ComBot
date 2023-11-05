import os
from . import *
from playwright.async_api import async_playwright
from urllib.parse import quote
from secrets import token_hex


@Client.on_command("carbon")
async def createCarbon(ctx: BotContext[CommandEvent]):
    event = ctx.event.message
    text = ctx.event.params
    if not text:
        return await event.reply_text("Provide text to create carbon!")

    text = quote(text)
    message = await event.reply_text("Processing")
    async with async_playwright() as play:
        browser = await play.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(
                f"https://carbon.now.sh/?t=seti&wt=none&l=application%2Fx-sh&width=680&ds=true&dsyoff=20px&dsblur=68px&wc=true&wa=true&pv=56px&ph=56px&ln=false&fl=1&fm=Hack&fs=14px&lh=133%25&si=false&es=1x&wm=false&code={text}"
            )
        except TimeoutError:
            pass
        await page.locator('button:has-text("Export menu dropdown")').click()
        await page.wait_for_load_state("domcontentloaded")
        await page.locator("text=1x").click()
        async with page.expect_download() as download_info:
            await page.locator("text=PNG").click()
            download = await download_info.value
            imgfile = f"temp/{token_hex(8)}.png"
            await download.save_as(imgfile)
    await event.send(
        "Carbon",
        embed_message=EmbeddedMedia(
            imgfile,
            header_name="Carbon Bot",
            header_icon="https://img.icons8.com/?size=512&id=114320&format=png",
#            description="You can use @carbon_bot to generate ",
            title="Here is your carbon!",
 #           footer_title="Use @carbon_bot to generate such images!",
            footer_icon="",
            inline_fields=[[EmbedInlineField("", "", "*Output*")]],
        ),
    )
    await message.delete()
    os.remove(imgfile)
