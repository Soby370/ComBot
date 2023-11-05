from . import *
from database.community import IntializeCommunity


@Bot.on_command("economy")
async def enableEconomy(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if message.personal_chat:
        return
    com = IntializeCommunity(message.community_id)
    eco = com._com.child("economy")
    if com.economy:
        eco.delete()
        await message.reply_text("Disabled Economy settings!")
        return
    eco.set(True)
    await message.reply_text("Enabled Economy")

@Bot.on_command("addcredit", admin_filter)
async def addCredit(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    param = ctx.event.params
    reply = await message.get_replied_message()
    if not reply or reply.user.is_bot:
        return await message.reply_text("Reply to a user of which, you want to increment credits...")
    if not param:
        return await message.reply_text("Provide a credit amount to add to user!")
    param = int(param)
    com = IntializeCommunity(message.community_id)
    com.add_economy_credit(reply.user_id, param)
    await message.reply_text("Added credits to the user!") 
 
