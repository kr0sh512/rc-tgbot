import os
import sys
import telebot
import threading
from config import config, Messages
from telebot import types
from plugin.user import User
from plugin.admin import Admin, AdminMessages
from plugin.bot_instance import bot, BotCommands
from plugin.register import start_reg_name
from datetime import datetime, timedelta
import time


admin_id = config.ADMIN_ID


@bot.message_handler(commands=BotCommands.Start)
def start_message(message: types.Message):
    if Admin.is_admin(message.chat.id):
        help_message(message)

        return

    if User(message.chat.id).name is not None:
        user = User(message.chat.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                "Оставьте как есть!", callback_data="registration_skip"
            )
        )
        markup.add(
            types.InlineKeyboardButton(
                "Зарегестрироваться заново", callback_data="registration_change"
            )
        )

        bot.send_message(message.chat.id, Messages.ALREADY_REGISTERED)
        bot.send_message(
            message.chat.id,
            Messages.REGISTRATION_CONFIRM.format(
                user.name,
                user.age,
                "Парень" if user.gender == "man" else "Девушка",
                user.faculty,
                user.group,
            ),
            reply_markup=markup,
        )

        return

    for msg in Messages.WELCOME_LIST:
        bot.send_message(message.chat.id, msg)

    bot.send_message(message.chat.id, Messages.ENTER_NAME)
    bot.register_next_step_handler(message, start_reg_name)

    return


@bot.message_handler(commands=BotCommands.Help)
def help_message(message: types.Message):
    if not Admin.is_admin(message.chat.id):
        for msg in Messages.HELPS:
            bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, AdminMessages.ADMIN_HELP, parse_mode="HTML")

    return


@bot.message_handler(commands=BotCommands.Source)
def source(message: types.Message):
    bot.send_message(
        message.chat.id,
        "[Страничка бота на Github!](https://github.com/kr0sh512/rc-tgbot)\n\nСтарался раб профкомский [Дмитрий](https://t.me/kr0sh_512)",
        parse_mode="Markdown",
    )

    return


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: types.Message):
    help_message(message)


if __name__ == "__main__":
    print("/t--- Bot started ---")

    admins = Admin.get_all_admins()
    for admin in admins:
        bot.send_message(
            admin["user_id"],
            "Служебное сообщение: бот был перезапущен.",
        )

    # Test connection to the database
    try:
        User.get_all()
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")

    time_for_notif = config.DATE_START

    while True:
        if config.DATE_START - datetime.now() < timedelta(days=1):
            users = User.get_all()
            for user in users:
                bot.send_message(
                    user["user_id"],
                    "Напоминание, что наше мероприятие пройдёт уже завтра! Следите за новостями)",
                )

            admins = Admin.get_all_admins()
            for admin in admins:
                bot.send_message(
                    admin["user_id"],
                    "Отправлено напоминание о скором начале мероприятия.",
                )
        time.sleep(10)
