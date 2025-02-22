import telebot
import config
import threading

bot = telebot.TeleBot(
    config.BOT_TOKEN,
    colorful_logs=True,
)

threading.Thread(
    target=bot.infinity_polling,
    name="bot_infinity_polling",
    daemon=True,
).start()
