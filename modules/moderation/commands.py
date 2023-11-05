import datetime
from datetime import timedelta
from database.community import IntializeCommunity, NoWarnsFound
from . import *

def parseParam(time):
    timestamp = datetime.now().timestamp()
    if time.endswith("s"):
        timestamp *= 60 * 1000
    if time.endswith("m"):
        timestamp *= (60**2) * 1000
    elif time.endswith("h"):
        timestamp *= (60**2) * 1000
    elif time.endswith("d"):
        timestamp *= (60**2) * 1000 * 24
    else:
        return
    timestamp *= int(time[:-1])
    return int(timestamp)

def time_parser(time_str):
    time_parts = time_str.split(':')
    days = hours = minutes = 0

    for part in time_parts:
        if part.endswith("d"):
            days = int(part[:-1])
        elif part.endswith("h"):
            hours = int(part[:-1])
        elif part.endswith("m"):
            minutes = int(part[:-1])

    delta = timedelta(days=days, hours=hours, minutes=minutes)
    past_time = datetime.now() + delta
    return int(past_time.timestamp())


@Client.on_command("restrict")
async def restrictUser(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not ctx.event.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(ctx):
        return await message.reply_text("Only Admins can use this command.")
    replied = await message.get_replied_message()
    if not replied:
        return await message.reply_text("Reply message to restrict the user.")
    timeslot = ctx.event.params or "1h"
    restrictedTimestamp = parseParam(ctx.event.params or timeslot)
    await ctx.restrict_user(
        ctx.event.community_id, True, replied.user_id , until_date=restrictedTimestamp
    )
    await message.reply_text(
        f"@{replied.user.username} has been restricted for {timeslot}!"
    )


@Client.on_command("unrestrict")
async def unrestrictUser(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(ctx):
        return await message.reply_text("Only Admins can use this command.")
    replied = await message.get_replied_message()
    if not replied:
        return await message.reply_text("Reply message to unrestrict the user.")
    await ctx.update_restricted_user(ctx.event.community_id, False, replied.user_id)
    await message.reply_text(f"@{replied.user.username}'s restriction are now removed!")


@Client.on_command("ban")
async def banUser(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(None, ctx):
        return await message.reply_text("Only Admins can use this command.")
    replied = await message.get_replied_message()
    if replied:
        sender_id = replied.user_id
    else:
        sender_id = message.user_id
    banInfo = await ctx.ban_user(message.community_id, sender_id)
    if banInfo.banned:
        await message.reply_text(f"Banned {replied.user.name} successfully!")


@Client.on_command("unban")
async def unBanUser(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(ctx):
        return await message.reply_text("Only Admins can use this command.")
    replied = await message.get_replied_message()
    if not replied:
        return await message.reply_text("Reply message to unban the user.")
    try:
        await ctx.unban_user(
            True, message.community_id, replied.user.id, replied.user_id
        )
        await message.reply_text(f"Banned {replied.user.name} successfully!")
    except Exception as er:
        await message.reply_text(f"Failed to unban user\n{er}")


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


@Client.on_command("promote")
async def promoteUser(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(ctx):
        return await message.reply_text("Only admins can use this command.")
    replied = await message.get_replied_message()
    print(replied, type(replied))
    if not (replied and not replied.user.is_bot):
        return await message.reply_text("Reply to a user message.")
    try:
        role = message.message.split()[0]
    except IndexError:
        return await message.reply_text("Provide role name to add user to it.")
    roles = await ctx.get_roles(message.community_id)
    role = list(filter(lambda x: x.name == role, roles))
    if not role:
        return await message.reply_text(f"Role {role} not found!")
    await ctx.add_member_to_role(
        community_id=message.community_id,
        member_id=replied.user_id,
        role_id=role[0].id,
        user_id=replied.user_id,
        user=replied.user,
    )
    await message.reply_text(f"Added {replied.user.name} to the role {role}")


@Client.on_command("demote")
async def demoteUser(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(ctx):
        return await message.reply_text("Only admins can use this command.")
    replied = await message.get_replied_message()
    if not replied or replied.user.is_bot:
        return await message.reply_text("Reply to a user message.")
    roles = await ctx.get_roles(message.community_id)
    for role in roles:
        members = await ctx.get_members(role_id=role.id)
        isPresent = list(filter(lambda x: x.user_id == replied.user_id, members))
        if isPresent:
            roleMember = isPresent[0]
            await ctx.delete_role_member(
                id=roleMember.id, member_id=roleMember.member_id, role_id=role.id
            )
    await message.reply_text(f"Removed {replied.user.name} from all roles!")

@Client.on_command("warn")
async def warnUser(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(ctx):
        return await message.reply_text("Only Admins can use this command.")
    replied = await message.get_replied_message()
    if not replied:
        return await message.reply_text("Reply message to unrestrict the user.")
    reason = ctx.event.params or None
    cdB = IntializeCommunity(ctx.event.community_id)
    await cdB.add_warns(replied.user_id, reason=reason)
    data = await cdB.get_warns(replied.user_id)
    if int(data["count"]) > 3:
        restrictedTimestamp = time_parser("1d")
        await ctx.restrict_user(
            ctx.event.community_id, True, replied.user_id , until_date=restrictedTimestamp
        )
        await cdB.reset_warns(replied.user_id)
        return await ctx.event.message.reply_text(f"*Restricted {replied.user.name} For {data['reason']} For 1 Day*")
    await message.reply_text(
        f"*WARNING :* {data['count']}/4\n*To :* {replied.user.name}\n*Be Careful !!!*\n\n*Reason* : {data['reason']}"
    )

@Client.on_command("getwarn")
async def getwarnUser(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(ctx):
        return await message.reply_text("Only Admins can use this command.")
    replied = await message.get_replied_message()
    if not replied:
        return await message.reply_text("Reply message to unrestrict the user.")
    cdB = IntializeCommunity(ctx.event.community_id)
    try:
        data = await cdB.get_warns(replied.user_id)
        return await message.reply_text(
            f"*WARNS :* {data['count']}/4\n*To :* {replied.user.name}\n\n*Reason* : {data['reason']}"
        )
    except NoWarnsFound:
        return await message.reply_text("No Warns Found On Given User!")

@Client.on_command("addprofanityfilter")
async def _add_prof(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    print(ctx.event.community_id, ctx.event.group_id)
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not message.group_id:
        return await message.reply_text("Use this command in a Community's Group.")
    if not await admin_check(ctx):
        return await message.reply_text("Only Admins can use this command.")
    await ctx.enable_messages(ctx.event.community_id, ctx.event.group_id)
    await message.reply_text("Succesfully Added This Group In Profanity Filter Watch!")