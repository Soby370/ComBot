import requests, asyncio
from . import Client as app, BotContext, CommandEvent, MessageEvent
from swibots import EmbeddedMedia, EmbedInlineField
from io import BytesIO

POKE = {}


@app.on_command("pokemon")
async def guessthepokemon(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    proc = await message.send("Processing...")
    try:
        response = requests.get(
            "https://api.aniket091.xyz/pokemon"
        )
        status = response.status_code
    except Exception as er:
        print(er)
        status = 0
    if status != 200:
        return await message.send(
            "There was an error fetching the pokemon data. Please try again later."
        )

    data = response.json()
    pokemon = data["data"]

    file = BytesIO(file.content)
    file.name = "image.png"
    # Create an embed for the question
    embed = EmbeddedMedia(
        thumbnail=file,
        header_name="Guess Pokemon",
        header_icon="https://img.icons8.com/?size=1x&id=O8qZGG8hWatE&format=png",
        title="Who's The Pokemon?",
        description="The more you hunt, more your hunting skills will grow!",
        #            description=f"**Image:** {pokemon['questionImage']}",
        footer_icon="Be the Pokemon Hunter",
        inline_fields=[
            [EmbedInlineField("", pokemon["types"], "Type")],
            [EmbedInlineField("", pokemon["abilities"], "Abilities")],
        ],
        footer_title="Throw your pokeball!",
    )
    await proc.delete()
    # Send the embed and start the game
    msg = await message.send("Guess Pokemon", embed_message=embed)

    answer = pokemon["name"]
    chat_id = message.user_id or message.group_id or message.channel_id

    if POKE.get(chat_id):
        await POKE[chat_id]["message"].delete()
        await message.send("Starting new...")

    POKE[chat_id] = {"answer": answer, "message": msg}

    async def check():
        await asyncio.sleep(5 * 60)
        if POKE.get(chat_id):
            await message.send("Timeout!\nEnding Game...")
            del POKE[chat_id]

    await check()


@app.on_command("cancelpokemon")
async def cancelgoing(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    chat_id = message.user_id or message.group_id or message.channel_id
    if POKE.get(chat_id):
        if POKE[chat_id]["message"].user_id == message.user_id:
            await POKE[chat_id]["message"].delete()
            del POKE[chat_id]
    else:
        await message.respond("Game is not active currently!")
        return
    await message.send("Cancelled!")


@app.on_message()
async def onMessage(ctx: BotContext[MessageEvent]):
    message = ctx.event.message
    chat_id = message.user_id or message.group_id or message.channel_id
    if POKE.get(chat_id):
        answer = POKE[chat_id]["answer"]
        if answer.lower() != message.message.lower():
            await message.send(
                "Incorrect Answer!\nTry Again, Embrace your hunting skills!"
            )
            return
        await message.send(
            f"*{message.user.name}* you got it!\nYou are the Pokemon Hunter!"
        )
        #        await POKE[chat_id]["message"].delete()
        del POKE[chat_id]
