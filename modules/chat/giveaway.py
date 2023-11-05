from . import Client, BotContext, CommandEvent, Config, admin_check
import asyncio, os, secrets, random
import contextlib
from swibots import (
    regexp,
    CallbackQueryEvent,
    InlineKeyboardButton,
    InlineMarkup,
)

from database.community import IntializeCommunity, AlreadyParticipated
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

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
    return datetime.fromtimestamp(int(past_time.timestamp()))

async def end_up_giveaway(giveaway_id, dB: IntializeCommunity, chat_id): # haven't tested this
    try:
        data = await dB.get_giveaways(giveaway_id)
        par = data["participants"]
        winners = []
        for _ in range(data["winner_count"]):
            u = random.choice(par)
            par.remove(u)
            winners.append(u)
        txt = f"*{data['giveaway_title']} GiveAway Winners:* \n\n"
        for w in winners:
            txt += f"> @{w}\n"
        txt += f"\n *Won {data['reaward_text']}*"
        await Client.send_text(txt, channel=chat_id)
    except Exception as err:
        print(err)

@Client.on_command("addgiveaway")
async def _add_giveaway(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(ctx):
        return await message.reply_text("Only Admins can use this command.")
    title, time, reaward_text, winner_count = ctx.event.params.split("|")
    uid = secrets.token_hex(nbytes=5)
    cdB = IntializeCommunity(message.community_id)
    await cdB.add_giveaway(reaward_text, uid, title, int(winner_count))
    scheduler.add_job(end_up_giveaway, "date", run_date=time_parser(time), args=(uid, cdB, message.group_id or message.channel_id), id=uid)
    await message.reply_text(f"*{title} GiveAway Started Today*\n*Rewards:* {reaward_text}\n*End At:* `{time_parser(time).strftime('%a %b %d %H:%M:%S %z %Y')}`")

@Client.on_command("deletegiveaway")
async def _del_giveaway(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    if not await admin_check(ctx):
        return await message.reply_text("Only Admins can use this command.")
    cdB = IntializeCommunity(message.community_id)
    data = await cdB.get_giveaways()
    _lst = [InlineKeyboardButton(text=data[x]['giveaway_title'], callback_data=f"dga:{x}:{message.user_id}") for x in data.keys()]
    button = list(zip(_lst[::3], _lst[1::3], _lst[2::3]))
    button.append(
        [_lst[-(z + 1)] for z in reversed(range(len(_lst) - ((len(_lst) // 3) * 3)))]
    )
    await message.reply_text("Choose GiveAway You Want To Delete:", inline_markup=InlineMarkup(button))

@Client.on_command("participate")
async def _participate(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if not message.community_id:
        return await message.reply_text("Use this command in a community.")
    cdB = IntializeCommunity(message.community_id)
    data = await cdB.get_giveaways()
    _lst = [InlineKeyboardButton(text=data[x]['giveaway_title'], callback_data=f"par:{x}:{message.user.username}:{message.user_id}") for x in data.keys()]
    button = list(zip(_lst[::3], _lst[1::3], _lst[2::3]))
    button.append(
        [_lst[-(z + 1)] for z in reversed(range(len(_lst) - ((len(_lst) // 3) * 3)))]
    )
    await message.reply_text("Choose GiveAway You Want To Participate:", inline_markup=InlineMarkup(button))

@Client.on_callback_query(regexp(r"dga:"))
async def ParonCallback(ctx: BotContext[CallbackQueryEvent]):
    data = ctx.event.message.callback_data.split(":")
    uid, user_id = data[1], int(data[2])
    if user_id != int(ctx.event.action_by_id):
        return
    cdB = IntializeCommunity(ctx.event.community_id)
    try:
        await cdB.delete_giveaway(uid)
        with contextlib.suppress(Exception):
            scheduler.remove_job(uid)
        await ctx.event.message.edit_text("Sucessfully Deleted On Clicked GiveAway!", inline_markup=None)
    except Exception as err:
        print(err)
        await ctx.event.message.edit_text("Unable To Delete On Clicked GiveAway!", inline_markup=None)

@Client.on_callback_query(regexp(r"par:"))
async def ParonCallback(ctx: BotContext[CallbackQueryEvent]):
    data = ctx.event.message.callback_data.split(":")
    uid, user_name, user_id = data[1], data[2], int(data[3])
    if user_id != int(ctx.event.action_by_id):
        return
    cdB = IntializeCommunity(ctx.event.community_id)
    try:
        await cdB.add_participant_in_giveaway(uid, user_name)
        await ctx.event.message.edit_text("Sucessfully Participated On Clicked GiveAway!", inline_markup=None)
    except AlreadyParticipated:
        await ctx.event.message.edit_text("You Already Paricipated In This GiveAway!", inline_markup=None)

scheduler.start()