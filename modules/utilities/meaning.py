import contextlib
import requests
from . import Client, CommandEvent, BotContext


@Client.on_command("meaning")
async def getMean(ctx: BotContext[CommandEvent]):
    event = ctx.event.message
    if not ctx.event.params:
        return await event.reply_text("Provide word to get meaning")
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{ctx.event.params}"
    out = requests.get(url).json()
    with contextlib.suppress(KeyError, TypeError):
        return await event.reply_text(f'**{out["title"]}**')
    defi = out[0]["meanings"][0]["definitions"][0]
    ex = defi["example"] if defi.get("example") else "None"
    text = f'• *Word :* `{ctx.event.params}`\n• *Meaning :* __{defi["definition"]}__\n\n• *Example :* __{ex}__'
    if defi.get("synonyms"):
        text += (
            f"\n\n• *Synonyms :*"
            + "".join(f" {a}," for a in defi["synonyms"])[:-1][:10]
        )
    if defi.get("antonyms"):
        text += (
            f"\n\n*Antonyms :*" + "".join(f" {a}," for a in defi["antonyms"])[:-1][:10]
        )
    await event.reply_text(text)
