from . import Client, BotContext, CommandEvent, Config, admin_filter
import asyncio, os
from swibots import (
    MemberJoinedEvent,
    Message,
    regexp,
    MemberLeftEvent,
    CallbackQueryEvent,
    InlineKeyboardButton,
    InlineMarkup,
)
from PIL import Image
from PIL import ImageDraw, ImageFont

from secrets import token_hex
from datetime import datetime
from database.community import IntializeCommunity

WELCOME_MSG = """Welcome *{name}* to {community}!

Click the below button to start messaging!"""

currentUsers = {}


async def validate_user(
    wait_time: int, community_id: str, user_id: int, message: Message
):
    await asyncio.sleep(wait_time)
    user = await Client.get_restricted_user(community_id, user_id)
    if user and user.restricted:
        await Client.ban_user(community_id, user_id)
        await Client.unban_user(True, community_id, id=0, user_id=user_id)
        await message.delete()


# todo: handle user leave and delete messagge

def createImage(name):
    img = Image.open("assets/welcome.png")

    font = ImageFont.truetype(
        "./assets/BungeeSpice-Regular.ttf",
        size=100,
    )
    I1 = ImageDraw.Draw(img)

    I1.text(
        (img.width / 2, img.height / 1.35),
        name,
        fill="lightblue",
        font=font,
        anchor="mm",
    )
    file = f"{token_hex(6)}.png"
    img.save(file)
    return file

@Client.on_member_joined()
async def onJoinEvent(ctx: BotContext[MemberJoinedEvent]):
    user_id = ctx.event.user.id
    community_id = ctx.event.community_id
    dbCom = IntializeCommunity(community_id)
    welcome = await dbCom.get_welcome()
    if not welcome:
        return
    chat_id = welcome["notify_channel_id"]
    isGroup = welcome["is_group"]
    now = datetime.now().timestamp()
    file = createImage(ctx.event.action_by.name)
    verify = welcome.get("verify")
    if not verify:
        txt = welcome['text'] or f"🥤 Welcome @{ctx.event.action_by.username}\n\n🎉 Follow the rules and enjoy the chat!"
    else:
        txt = welcome["text"] or WELCOME_MSG.format(
            name=ctx.event.user.name, community=ctx.event.community.name
        )
    newMsg = await ctx.send_message(
        community_id=community_id,
        group_id=chat_id if isGroup else None,
        channel_id=None if isGroup else chat_id,
        document=file,
        thumb=file,
        message=txt,
        description=os.path.basename(file),
        inline_markup=InlineMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Click to verify",
                        callback_data=f"verify:{community_id}:{user_id}",
                    )
                ]
            ]
        ) if verify else InlineMarkup(
            [[InlineKeyboardButton("Thanks for joining")]]
        ),
    )
    os.remove(file)
    if not verify:
        return
    await ctx.restrict_user(
        community_id,
        restricted=True,
        user_id=user_id,
        until_date=int(now) + 15 * 1000 * 60,
    )
    if not currentUsers.get(community_id):
        currentUsers[community_id] = {}
    if not currentUsers[community_id].get(user_id):
        currentUsers[community_id][user_id] = newMsg.id
    await validate_user(15 * 60, community_id, user_id, newMsg)


@Client.on_member_left()
async def handleLeave(ctx: BotContext[MemberLeftEvent]):
    community_id = ctx.event.community_id
    if not currentUsers.get(community_id):
        return
    user_id = ctx.event.user_id
    if msgId := currentUsers[community_id].get(user_id):
        await Client.delete_message(msgId)


@Client.on_callback_query(regexp(r"verify:(.*)"))
async def onCallback(ctx: BotContext[CallbackQueryEvent]):
    data = ctx.event.message.callback_data.split(":")[1:]
    community_id = data[0]
    user_id = int(data[1])
    if user_id != int(ctx.event.action_by_id):
        return
    await Client.update_restricted_user(community_id, restricted=False, user_id=user_id)
    await ctx.event.message.edit_text(
        f"🥤 Welcome @{ctx.event.action_by.username}\n\n🎉 Follow the rules and enjoy the chat!",
        inline_markup=InlineMarkup(
            [[InlineKeyboardButton("Thanks for joining", url=" ")]]
        ),
    )
    com = IntializeCommunity(community_id)
    com.add_economy_credit(user_id, 10)


@Client.on_command("setwelcome", filter=admin_filter)
async def setWelcome(ctx: BotContext[CommandEvent]):
    group_id = ctx.event.group_id or ctx.event.channel_id
    if not group_id:
        return
    event = ctx.event.message
    param = ctx.event.params
    replied = await ctx.event.message.get_replied_message()
    community = IntializeCommunity(event.community_id)
    await community.set_welcome(
        text=replied.message if replied else "",
        notify_channel_id=group_id,
        is_group=bool(ctx.event.group_id),
        verify=param.lower() == "verify"
    )
    await event.reply_text("Updated welcome!")


@Client.on_command("deletewelcome", filter=admin_filter)
async def deleteWelcome(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if message.personal_chat:
        return
    community_id = message.community_id
    com = IntializeCommunity(community_id)
    com.delete_welcome()
    await message.reply_text("Removed welcome!")
