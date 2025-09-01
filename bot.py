from telebot import TeleBot, types

BOT_TOKEN = "8394371002:AAHp9f19o2xb67duYLcJrJotfCDpAHu_GqQ"
bot = TeleBot(BOT_TOKEN, parse_mode="HTML")

APP_URL = "https://test-dtca.onrender.com"

@bot.message_handler(commands=["start"])
def start(msg):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    webapp_btn = types.KeyboardButton("🚀 Запустить Mini App", web_app=types.WebAppInfo(url=APP_URL))
    kb.add(webapp_btn)
    bot.send_message(
        msg.chat.id,
        "Нажмите кнопку, чтобы открыть Mini App:",
        reply_markup=kb
    )

@bot.message_handler(commands=["set"])
def set_buttons(msg):
    try:
        parts = msg.text.split()
        if len(parts) < 2:
            bot.reply_to(msg, "Укажи ID канала после команды.\nПример: <code>/set -1001234567890</code>")
            return

        channel_id = int(parts[1])

        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("✅ Read", url=f"{APP_URL}/post/en/read"),
            types.InlineKeyboardButton("🕒 Unread", url=f"{APP_URL}/post/en/unread")
        )
        kb.add(types.InlineKeyboardButton("📋 All", url=f"{APP_URL}/post/en/all"))

        bot.send_message(
            channel_id,
            "Выберите фильтр новостей:",
            reply_markup=kb
        )
        bot.reply_to(msg, f"Кнопки отправлены в канал {channel_id}")

    except Exception as e:
        bot.reply_to(msg, f"Ошибка: {e}")

bot.infinity_polling()