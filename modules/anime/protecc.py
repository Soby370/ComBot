from . import *
import random, asyncio
from io import BytesIO
from database import global_user
from fuzzywuzzy.process import fuzz
from datetime import datetime

GameHandler = {}


@Bot.on_command("enableprotecc", filters.community(None))
async def enableProtec(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    if not await ctx.check_messaging_enabled(
        community_id=m.community_id,
        group_id=m.group_id
    ):
        return await m.reply_text("Enable Instant messaging in current chat!\nThen use this command")

    from bot import DB

    wc = DB.child("WaifuComs")
    coms = wc.get() or []
    chat = [m.community_id, m.group_id or m.channel_id]
    if chat not in coms:
        coms.append(chat)
    else:
        return await m.reply_text("Waifu protect is already enabled in current chat!")
    wc.set(coms)
    await m.reply_text("Enabled Waifu Protect in current chat!")


@Bot.on_command("disableprotecc", filters.community(None))
async def disableProtec(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    from bot import DB

    wc = DB.child("WaifuComs")
    coms = wc.get() or []
    chat = [m.community_id, m.group_id or m.channel_id]
    if chat in coms:
        coms.remove(chat)
    else:
        return await m.reply_text("Waifu protect is already enabled in current chat!")
    wc.set(coms)
    await m.reply_text("Disabled Waifu protect!")


@Bot.on_command("harem")
async def getHarem(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    d = global_user(m.user_id).get() or []
    if not d:
        return await m.reply_text("Your harem list is empty!")
    message = "Here is your harem box!\n\n"
    for char in d:
        data = requests.get(f"https://api.jikan.moe/v4/characters/{char}").json()['data']
        message += f"<b>{data['name']}</b>\n- {data['url']}\n\n"
    await m.reply_text(message)

@Bot.on_command("protecc", filters.community(None))
async def proteccCommand(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    param = ctx.event.params
    if not param:
        return await m.reply_text("Provide a name to guess!")
    key = f"{m.community_id}:{m.channel_id or m.group_id}"
    if GameHandler.get(key) and GameHandler[key].get("isActive"):
        ratio = fuzz.partial_ratio(param.lower(), GameHandler[key]["name"].lower())
        if ratio >= 88:
            idd = GameHandler[key]["id"]
            await m.reply_text("You got it!\nIt has been added to your harem!")
            await GameHandler[key]["message"].delete()
            del GameHandler[key]["isActive"]
            del GameHandler[key]["message"]
            del GameHandler[key]["id"]
            user = global_user(m.user_id)
            data = user.get() or []
            if idd not in data:
                data.append(idd)
            user.set(data)
        elif ratio > 60:
            await m.reply_text("You are close! Think more to get it correct!")
        else:
            await m.reply_text("No, Keep trying...")
        return
    await m.reply_text("Protecc can be only be used after the waifu appears!")
    


@Bot.on_message(filters.community(None))
async def onComMessage(ctx: BotContext[MessageEvent]):
    from bot import DB

    m = ctx.event.message
    chat = [m.community_id, m.group_id or m.channel_id]
    coms = DB.child("WaifuComs").get() or []
    if chat not in coms:
        return
    key = f"{m.community_id}:{m.group_id or m.channel_id}"
    if GameHandler.get(key):
        old_time = datetime.fromtimestamp(GameHandler[key]["time"])
        now = datetime.now()
        if ((now - old_time).total_seconds() / 60**2) < GameHandler["wait"]:
            return
    data = requests.get("https://api.jikan.moe/v4/random/characters").json()
    image = BytesIO(requests.get(data["data"]["images"]["jpg"]["image_url"]).content)
    image.name = "file.png"

    name = data["data"]["name"]
    GameHandler[key] = data = {
        "wait": random.randint(8, 50),
        "time": datetime.now(),
        "name": name,
        "isActive": True,
        "id": data["data"]["mal_id"],
    }
    print(name)
    msg = await m.send(
        "*Guess Waifu*\nGuess it with /protecc characterName", document=image,
        thumb=image
    )
    data["message"] = msg
    await asyncio.sleep(3 * 60)
    if data.get("isActive"):
        del data["isActive"]
        await m.delete()
        await m.send("No-One guessed the waifu!")
