from . import Client, BotContext, CommandEvent, admin_check, admin_filter

@Client.on_command("del")
async def deleteMessage(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if message.community_id and not await admin_check(ctx):
        return await message.reply_text("Only admins can use this command.")
    replied = await message.get_replied_message()
    if not replied:
        return await message.reply_text("Reply to a message to delete it.")
    await ctx.delete_message(replied.id)
    await ctx.delete_message(message.id)