from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

CHANNELS = [
    {
        "username": "@Ahmad_Naguib_Al",
        "name": "قناة أحمد نجيب",
        "url": "https://t.me/Ahmad_Naguib_Al",
    },
    {
        "username": "@alawodi_10",
        "name": "قناة العوادي 10",
        "url": "https://t.me/alawodi_10",
    },
]


async def check_subscription(bot: Bot, user_id: int) -> bool:
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(channel["username"], user_id)
            if member.status in ["left", "kicked", "banned"]:
                return False
        except TelegramError:
            pass
    return True


async def send_subscription_prompt(update, context):
    keyboard = []
    for ch in CHANNELS:
        keyboard.append([InlineKeyboardButton(f"📢 اشترك في {ch['name']}", url=ch["url"])])
    keyboard.append(
        [InlineKeyboardButton("✅ اشتركت — تحقق الآن", callback_data="check_subscription")]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⚠️ *للاستخدام يجب الاشتراك في القناتين أولاً:*\n\n"
        "📢 قناة أحمد نجيب\n"
        "😂 قناة العوادي 10\n\n"
        "اشترك في القناتين ثم اضغط على زر التحقق 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
