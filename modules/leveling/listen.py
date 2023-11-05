import os, asyncio
from . import *
from .levels import ReverseLevels
from contextlib import suppress
from database.community import IntializeCommunity
from utils.imagehelper import create_level_thumb
from io import BytesIO
from asyncio import Queue
from secrets import token_hex

config = {}


@Bot.on_message(filters.communities)
async def messaent(ctx: BotContext[MessageEvent]):
    from bot import DB

    message = ctx.event.message

    data = DB.child("levelCommunities").get() or []

    if message.community_id not in data:
        return
    start_task = not config.get(message.community_id)

    if not config.get(message.community_id):
        config[message.community_id] = Queue()

    queue: Queue = config[message.community_id]

    async def processMessage(message):
        chat_user = (
            DB.child(message.community_id).child("Users").child(str(message.user_id))
        )
        com = IntializeCommunity(message.community_id)
        user = chat_user.get() or {}
        if not user:
            user["mcount"] = 1
            user["level"] = 0
        else:
            user["mcount"] += 1
        if message.replied_to_id:
            if "rcount" not in user:
                user["rcount"] = 1
            else:
                user["rcount"] += 1

        user_level = user["level"]
        m_count = user["mcount"]
        for level in ReverseLevels:
            if m_count > level.required and level.level > user_level:
                user["level"] = level.level
                thumb = create_level_thumb(
                    message.user.name,
                    level.level,
                    level.name,
                    file_name=f"{token_hex(5)}.png",
                )
                r_count = user.get("rcount", 0)
                user["rcount"] = 0
                await message.send(
                    "Level Upgrade",
                    embed_message=EmbeddedMedia(
                        thumbnail=thumb,
                        inline_fields=[
                            [
                                EmbedInlineField(
                                    icon="https://img.icons8.com/?size=256&id=12944&format=png",
                                    key="By participating in chat, you can level up more!",
                                    title="Note",
                                )
                            ]
                        ],
                        title=Bot.user.name,
                        header_name="Level Upgrade",
                        description=f"{message.user.name} got promoted to new level, {level.emoji} {level.name}",
                        header_icon="https://img.icons8.com/?size=256&id=ZhEeFTxx1s3Z&format=png",
                        footer_icon="https://img.icons8.com/?size=256&id=59023&format=png",
                        footer_title="level up to get exciting titles!",
                    ),
                )
                if com.economy:
                    com.add_economy_credit(
                        message.user_id, level.level * (2 if r_count > 100 else 4)
                    )
                    os.remove(thumb)
                break
        chat_user.set(user)

    async def processQueue():
        while not queue.empty():
            task = await queue.get()
            await task

        with suppress(KeyError):
            del config[message.community_id]

    await queue.put(processMessage(message))
    if start_task:
        asyncio.create_task(processQueue())
