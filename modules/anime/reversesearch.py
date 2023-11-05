from . import *
from io import BytesIO


@Bot.on_command("reverseanime")
async def reverseSearch(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    replied = await m.get_replied_message()
    if not (replied and replied.is_media):
        return await m.reply_text("Reply to a Image or GIF!")
    url = replied.media_link
    try:
        data = requests.get(f"https://api.trace.moe/search?url={url}").json()
    except Exception as er:
        LOG.exception(er)
        return await m.reply_text(f"ERROR: {er}")
    if not data.get("result"):
        return await m.reply_text("No Results found!")
    result = data["result"][0]
    await m.send(
        "*Anime Reverse*",
        embed_message=EmbeddedMedia(
            thumbnail=result["image"],
            title=ctx.user.name,
            header_name="Anime Reverse",
            description=f"Use @{ctx.user.user_name} to reverse search anime!",
            inline_fields=[
                [
                    EmbedInlineField(
                        "https://img.icons8.com/?size=256&id=1FE2HGszFS4w&format=png",
                        result["filename"],
                        "Anime",
                    ),
                    EmbedInlineField(
                        "https://img.icons8.com/?size=50&id=bjHuxcHTNosO&format=png",
                        round(result["similarity"], 2),
                        "Similarity",
                    ),
                ],
                [
                    EmbedInlineField(
                        "https://img.icons8.com/?size=256&id=JrbE13EfhZWo&format=png",
                        result["episode"],
                        "Episode",
                    ),
                    EmbedInlineField(
                        "", f"{result['from']*1000} to {result['to']*1000}", "Frame"
                    ),
                ],
            ],
            header_icon="https://img.icons8.com/?size=256&id=1FE2HGszFS4w&format=png",
            footer_title=result["filename"],
            footer_icon="https://img.icons8.com/?size=50&id=xZiTPdO57ltQ&format=png",
        ),
    )
    vid = result["video"]
    file = BytesIO(requests.get(vid).content)
    file.name = "video.mp4"
    thumb = BytesIO(requests.get(result["image"]).content)
    thumb.name = "file.png"
    await m.send(
        result["filename"], document=file, description=result["filename"], thumb=thumb
    )
