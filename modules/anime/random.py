from . import *


def randomHandler(key: str):
    async def handler(ctx: BotContext[CommandEvent]):
        message = ctx.event.message
        try:
            data = requests.get(f"https://api.jikan.moe/v4/random/anime").json()
            data = data["data"]
        except Exception as er:
            LOG.exception(er)
            await message.reply_text(
                f"Something went wrong while fetching {key} info..."
            )
            return
        if not data:
            return await message.reply_text("No results found!")
        await sendEmbedAnime(data, message, ctx.user.name, f"Random {key.capitalize()}")
    return handler


Bot.add_handler(CommandHandler("randomanime", randomHandler("anime")))
Bot.add_handler(CommandHandler("randommanga", randomHandler("manga")))
