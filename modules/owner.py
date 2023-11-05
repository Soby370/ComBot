import os, sys
from . import *


@Bot.on_command("restart", filter=filters.user(Config.OWNER_ID))
async def restartBot(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    await message.reply_text("Restarting bot!")
    os.execl(sys.executable, **sys.argv)
