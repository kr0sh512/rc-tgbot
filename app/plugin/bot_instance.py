import telebot
from config import config
import threading


class BotCommands:
    Start = ["start", "s"]
    Help = ["help", "h"]


bot = telebot.TeleBot(
    config.API_TOKEN,
    colorful_logs=True,
)

threading.Thread(
    target=bot.infinity_polling,
    name="bot_infinity_polling",
    daemon=True,
).start()
