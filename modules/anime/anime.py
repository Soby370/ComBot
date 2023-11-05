from . import *
from typing import Dict


def searchHandler(key, command=None):
    if not command:
        command = key

    async def handler(ctx: BotContext[CommandEvent]):
        message = ctx.event.message
        param = ctx.event.params

        if not param:
            return await message.reply_text("Provide something to search..")
        try:
            data = requests.get(
                f"https://api.jikan.moe/v4/{key}?q={param}&sfw=true&limit=1"
            ).json()
            data = data["data"]
        except Exception as er:
            LOG.exception(er)
            await message.reply_text(
                f"Something went wrong while fetching {key} info..."
            )
            return
        if not data:
            return await message.reply_text("No results found!")
        data = data[0]
        await (sendCharacter if key == "characters" else sendEmbedAnime)(
            data, message, ctx.user.name, f"Search results for {param}"
        )

    return Bot.add_handler(CommandHandler(command, handler))


def topHandler(key: str, command: str = None):
    if not command:
        command = key

    async def getTopAnime(ctx: BotContext[CommandEvent]):
        m = ctx.event.message
        try:
            data = requests.get(f"https://api.jikan.moe/v4/top/{key}").json()
            data = data["data"]
        except Exception as er:
            LOG.exception(er)
            await m.reply_text(f"Something went wrong while fetching {key} info...")
            return
        message = "🤩 Here is a list of top animes!\n\n"
        for index, anime in enumerate(data[:10], start=1):
            message += f"{index}. <b>{anime.get('title', '')}</b> [<copy>{anime['score']}</copy>]\n" 
        await m.reply_text(message)
    return Bot.add_handler(CommandHandler(command, getTopAnime))


searchHandler("anime")
searchHandler("manga")
searchHandler("characters", "character")

topHandler("anime", "topanime")
topHandler("manga", "topmanga")
