from swibots import (
    BotContext,
    CommandEvent,
    Message,
    CallbackQueryHandler,
    MessageEvent,
    CallbackQueryEvent,
    EmbeddedMedia,
    InlineMarkup,
    InlineKeyboardButton,
    regexp,
    EmbedInlineField,
    CommandHandler,
    MessageHandler,
    admin
)
from swibots import filters
from bot import Bot, Config, LOG

Client = app = Bot

async def admin_check(self, ctx: BotContext[CommandEvent]):
    if not ctx.event.community_id:
        return
    event = ctx.event.message
    try:
        return await ctx.is_admin(event.community_id, event.user_id)
    except Exception as er:
        print(er)
    return False

admin_filter = filters.create(admin_check, "admin_filter")

async def onCommunityFailure(_, ctx: BotContext[CommandEvent]):
    await ctx.event.message.reply_text("Use this command in community!")

filters.community.onFailure = onCommunityFailure