from . import *
import requests
from akinator.async_aki import Akinator
from typing import Dict
from io import BytesIO


class AkinatorHandler:
    def __init__(self) -> None:
        self._akinators: Dict[int, Akinator] = {}
        Bot.add_handler(CommandHandler("akinator", self.command))
        Bot.add_handler(CallbackQueryHandler(self.handle_callback, regexp(r"aka(.*)")))

    def getMarkup(self, message_id):
        return InlineMarkup(
            [
                [
                    InlineKeyboardButton(
                        text, callback_data=f"aka-{message_id}-{text.replace(' ', '_')}"
                    )
                    for text in ["Yes", "No", "Idk"]
                ],
                [
                    InlineKeyboardButton(
                        text, callback_data=f"aka-{message_id}-{text.replace(' ', '_')}"
                    )
                    for text in ["Probably", "Probably not"]
                ],
            ]
        )

    async def handle_callback(self, ctx: BotContext[CallbackQueryEvent]):
        query = ctx.event.callback_data.split("-")
        message_id, answer = int(query[1]), query[2].replace("_", " ")
        try:
            akinator = self._akinators[message_id]
            q = await akinator.answer(answer)
        except KeyError:
            await ctx.event.answer(
                "Game is not active anymore!\nStart a new one!", show_alert=True
            )
            await ctx.event.message.delete()
            return
        except Exception as er:
            await ctx.event.answer(str(er), show_alert=True)
            return

        if akinator.progression >= 80:
            try:
                await akinator.message.delete()
            except Exception:
                pass
            await akinator.win()
            gs = akinator.first_guess
            img = BytesIO(requests.get(gs["absolute_picture_path"]).content)
            img.name = "image.png"
            await akinator.message.reply_media(
                "It's " + gs["name"] + "\n " + gs["description"], document=img
            )
            return
        await akinator.message.edit_text(q, inline_markup=self.getMarkup(message_id))

    async def command(self, ctx: BotContext[CommandEvent]):
        message = ctx.event.message
        com = None
        if message.community_id:
            com = IntializeCommunity(message.community_id)
            credit = com.get_user_credit(message.user_id)
            if com.economy and (
                credit and credit < 5
            ):
                return await message.reply_text(
                    f"Your economy score [{credit}] is too low!"
                )

        akinator = self._akinators[message.id] = Akinator()
        m = akinator.message = await message.reply_media(
            "Akinator Game", document="assets/akinator.png"
        )
        try:
            q = await akinator.start_game()
        except Exception as er:
            LOG.exception(er)
            return await m.edit_text("Akinator servers are down!\nTry again later!")
        await akinator.message.edit_text(q, inline_markup=self.getMarkup(message.id))
        if com:
            com.reduce_economy_credit(message.user_id, 2)


AkinatorHandler()
