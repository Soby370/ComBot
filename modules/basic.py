import requests, json
from . import Bot
from database.community import IntializeCommunity
from swibots import (
    BotContext,
    CommandEvent,
    EmbeddedMedia,
    EmbedInlineField,
    MessageEvent,
    Message,
    filters,
)
from io import BytesIO


@Bot.on_command("start")
async def sendStart(ctx: BotContext[CommandEvent]):
    await ctx.event.message.send(
        "Start Message",
        embed_message=EmbeddedMedia(
            thumbnail=None,
            title=Bot.user.name,
            header_name="HELP Menu",
            description="Hi, Welcome to Web3family Assistant!",
            footer_icon="https://cdn08.chiheisen.app/1001903060952/14557",
            footer_title="Thanks for using me!",
            header_icon="https://img.icons8.com/?size=256&id=1H52efUsDX7A&format=png",
            inline_fields=[
                [
                    EmbedInlineField(
                        "https://img.icons8.com/?size=256&id=23280&format=png",
                        "ban, unban\n",
                        "Admins",
                    ),
                    EmbedInlineField(
                        key="restrict, unrestrict\n",
                        title=" ",
                        icon="https://img.icons8.com/?size=256&id=0afdeZSQQa96&format=png",
                    ),
                ],
                [
                    EmbedInlineField(
                        "https://img.icons8.com/?size=50&id=jSzptZca0mlE&format=png",
                        "anime\nrandomanime\nmanga\nrandommanga\ncharacter\n",
                        "Anime",
                    ),
                    EmbedInlineField("", "waifu\npat\nslap\nreverseanime", "Other"),
                ],
                [
                    EmbedInlineField(
                        "https://img.icons8.com/?size=256&id=jByggJU3XaEM&format=png",
                        "blackjack\n",
                        "Games",
                    ),
                    EmbedInlineField(
                        "https://img.icons8.com/?size=256&id=eQoYCq7PgMch&format=png",
                        key="Play Akinator",
                        title="akinator\n",
                    ),
                ],
                [
                    EmbedInlineField(
                        "https://img.icons8.com/?size=256&id=19411&format=png",
                        "addwelcome\ndeletewelcome\n",
                        "Welcome",
                    ),
                    EmbedInlineField(
                        "https://img.icons8.com/?size=256&id=yp5FEyT7rfET&format=png",
                        "addprofanityfilter\n",
                        "Profanity Check",
                    ),
                ],
                [
                    EmbedInlineField(
                        icon="https://img.icons8.com/?size=256&id=wuSvVpkmKrXV&format=png",
                        title="Giveaways",
                        key="addgiveaway\ndeletegiveaway\nparticipate\n",
                    ),
                    EmbedInlineField(
                        "https://img.icons8.com/?size=256&id=9d0casenOiHS&format=png",
                        title="Leveling",
                        key="enablelevel\ndisablelevel\n",
                    ),
                ],
                [
                    EmbedInlineField(
                        "https://img.icons8.com/?size=50&id=Yo9kOcztQ9xn&format=png",
                        key="economy\n",
                        title="Economy",
                    ),
                    EmbedInlineField(
                        "https://img.icons8.com/?size=50&id=1XKFBJvUFKTk&format=png",
                        title="For Owner",
                        key="addcredit\n",
                    ),
                ],
                [
                    EmbedInlineField(
                        icon="https://img.icons8.com/?size=256&id=13917&format=png",
                        key="qr\nimage\ncarbon\nwebshot",
                        title="Utilities",
                    ),
                    EmbedInlineField(
                        icon="https://img.icons8.com/?size=256&id=79UfeEN6JkZ8&format=png",
                        key="ipinfo\nuserinfo\ngadget\nmeaning",
                        title=" ",
                    ),
                ],
            ],
        ),
    )


@Bot.on_command("userinfo")
async def getUserInfo(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    if message.replied_to_id:
        replied = await message.get_replied_message()
        user = replied.user
    elif ctx.event.params:
        try:
            user_id = int(ctx.event.params)
            user = await ctx.get_user(user_id)
        except TypeError:
            return
    else:
        user = message.user
    media = None
    if user.image_url:
        media = BytesIO(requests.get(user.image_url).content)
        media.name = "image.png"
    response = f"""*User Info*\n\n
*Name:* {user.name}
*Username:* {user.username}
*UserID:* <copy>{user.id}</copy>
"""
    if user.is_bot:
        response += "\n*Bot*: True"
    if message.community_id:
        com = IntializeCommunity(message.community_id)
        user = com._com.child("Users").child(str(message.user_id)).get() or {}
        if user.get("mcount"):
            response += f"\n*Messages in community*: {user['mcount']}"
        if com._com.child("economy").get():
            response += f"\n*Credits Available*: {com.get_user_credit(message.user_id)}"
    await message.reply_text(response, document=media, thumb=media)


@Bot.on_command("json")
async def jsonCommand(ctx: BotContext[CommandEvent]):
    await ctx.event.message.reply_text(
        f"`{json.dumps(ctx.event.message.to_json(), indent=4)}`"
    )
