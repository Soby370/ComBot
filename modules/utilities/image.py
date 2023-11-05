import cv2, os
from . import *
import numpy as np
from secrets import token_hex


@Client.on_command("image")
async def processImageMagic(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    replied = await message.get_replied_message()
    if not (replied and replied.is_media):
        return await message.reply_text("Reply to an Image!")
    msg_id = replied.id
    await message.reply_text(
        "🎉 Choose effect you wish to add!",
        inline_markup=InlineMarkup(
            [
                [
                    InlineKeyboardButton("Gray 📷", callback_data=f"gray_{msg_id}"),
                    InlineKeyboardButton("Blur 👀", callback_data=f"blur_{msg_id}"),
                    InlineKeyboardButton("Danger 😱", callback_data=f"danger_{msg_id}"),
                ],
                [
                    InlineKeyboardButton("Quad 😵‍💫", callback_data=f"quad_{msg_id}"),
                    InlineKeyboardButton("Mirror 🪞", callback_data=f"mirror_{msg_id}"),
                    InlineKeyboardButton("Flip 💫", callback_data=f"flip_{msg_id}"),
                ],
                [
                    InlineKeyboardButton("Sketch 🖌️", callback_data=f"sketch_{msg_id}"),
                    InlineKeyboardButton("Cartoon 🐰", callback_data=f"toon_{msg_id}"),
                ],
                [
                    InlineKeyboardButton(
                        "Negative 🎩", callback_data=f"negative_{msg_id}"
                    ),
                ],
            ]
        ),
    )


async def process_file(file, match, event: Message):
    msg = await event.send("Processing!\nThis may take a while!")
    in_image = cv2.imread(file)
    if match == "gray":
        image = cv2.cvtColor(in_image, cv2.COLOR_BGR2GRAY)
    elif match == "blur":
        image = cv2.GaussianBlur(in_image, (35, 35), 0)
    elif match == "negative":
        image = cv2.bitwise_not(in_image)
    elif match == "danger":
        dan = cv2.cvtColor(in_image, cv2.COLOR_BGR2RGB)
        image = cv2.cvtColor(dan, cv2.COLOR_HSV2BGR)
    elif match == "mirror":
        ish = cv2.flip(in_image, 1)
        image = cv2.hconcat([in_image, ish])
    elif match == "flip":
        trn = cv2.flip(in_image, 1)
        ish = cv2.rotate(trn, cv2.ROTATE_180)
        image = cv2.vconcat([in_image, ish])
    elif match == "quad":
        in_image = cv2.imread(file)
        roid = cv2.flip(in_image, 1)
        mici = cv2.hconcat([in_image, roid])
        fr = cv2.flip(mici, 1)
        trn = cv2.rotate(fr, cv2.ROTATE_180)
        image = cv2.vconcat([mici, trn])
    elif match == "sketch":
        gray_image = cv2.cvtColor(in_image, cv2.COLOR_BGR2GRAY)
        inverted_gray_image = 255 - gray_image
        blurred_img = cv2.GaussianBlur(inverted_gray_image, (21, 21), 0)
        inverted_blurred_img = 255 - blurred_img
        image = cv2.divide(gray_image, inverted_blurred_img, scale=256.0)
    elif match == "toon":
        height, width, _ = in_image.shape
        samples = np.zeros([height * width, 3], dtype=np.float32)
        count = 0
        for x in range(height):
            for y in range(width):
                samples[count] = in_image[x][y]
                count += 1
        _, labels, centers = cv2.kmeans(
            samples,
            12,
            None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10000, 0.0001),
            5,
            cv2.KMEANS_PP_CENTERS,
        )
        centers = np.uint8(centers)
        ish = centers[labels.flatten()]
        image = ish.reshape(in_image.shape)
    else:
        return
    name = f"{token_hex(5)}.png"
    cv2.imwrite(name, image)
    await msg.delete()
    await event.send(
        "Image",
        embed_message=EmbeddedMedia(
            name,
            title="Response from @image_bot",
            description="You can use @image_bot to add different filters to your images!",
            header_icon="https://img.icons8.com/?size=512&id=114320&format=png",
            header_name="Image Bot",
            inline_fields=[[EmbedInlineField("", "", "Output")]],
            footer_title="Use @image_bot to add special effects!",
            footer_icon="",
        ),
    )
    os.remove(name)


@Client.on_callback_query(regexp(r"image(.*)"))
async def onCallback(ctx: BotContext[CallbackQueryEvent]):
    return
    callback = ctx.event.callback_data.split("_")
    messages = await ctx.get_messages(ctx.event.action_by_id)
    message = list(filter(lambda x: x.id == int(callback[-1]), messages))
    if not message:
        await ctx.event.message.delete()
        return
    message = message[0]
    file = await message.download("downloads")
    await process_file(file, callback[0], ctx.event.message)
