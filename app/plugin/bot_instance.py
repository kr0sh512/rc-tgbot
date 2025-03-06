import telebot
from config import config
import threading
import time


class BotCommands:
    Start = ["start", "s"]
    Help = ["help", "h", "помощь"]
    Source = ["source"]


original_send_message = telebot.TeleBot.send_message


def send_message_with_try_catch(self, chat_id, text, *args, **kwargs):
    try:
        return original_send_message(
            self, chat_id, text, parse_mode="HTML", *args, **kwargs
        )
    except Exception as e:
        print(f"Error sending message: {e}. Retrying in 5 seconds...")

        try:
            time.sleep(5)

            return original_send_message(
                self, chat_id, text, parse_mode="HTML" * args, **kwargs
            )
        except Exception as e:
            print(f"Second attempt failed: {e}")


telebot.TeleBot.send_message = send_message_with_try_catch

bot = telebot.TeleBot(
    config.API_TOKEN,
    colorful_logs=True,
)

threading.Thread(
    target=bot.infinity_polling,
    name="bot_infinity_polling",
    daemon=True,
).start()
