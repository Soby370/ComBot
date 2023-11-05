from . import *


@Bot.on_command("enablelevel")
async def enableLeveling(ctx: BotContext[CommandEvent]):
    from bot import DB

    message = ctx.event.message
    if message.personal_chat:
        return await message.reply_text("This command is for communities!")
    community = message.community_id
    #    data = DB.child(community).get() or {}
    #   data["levelsChat"] = {
    #      "chat_id": message.channel_id or message.group_id,
    #     "isGroup": bool(message.group_id),
    # }
    levelC = DB.child("levelCommunities").get() or []
    if community not in levelC:
        levelC.append(community)
        DB.child("levelCommunities").set(levelC)
    await message.reply_text("⭐ Enabled Leveling in current chat!\nNote: Enable instant messaging from community settings")


@Bot.on_command("disablelevel")
async def disableLeveling(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    community = message.community_id

    from bot import DB

    if message.personal_chat:
        return await message.reply_text("This command is restricted for communities!")
    # data = DB.child(message.community_id).get() or {}
    #    if data.get("levelsChat"):
    #       del data["levelsChat"]
    #      DB.child(message.community_id).set(data)
    # else:
    #    await message.reply_text("Leveling was not active in the current chat!")
    #   return
    levelC = DB.child("levelCommunities").get() or []

    if community in levelC:
        levelC.remove(community)
        DB.child("levelCommunities").set(levelC)
    else:
        await message.reply_text("Leveling was not active in the current chat!")
        return

    await message.reply_text("Disabled Leveling!")
