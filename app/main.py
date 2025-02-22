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
                user.gender,
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
    bot.send_message(
        message.chat.id,
        (
            Messages.HELP
            if not Admin.is_admin(message.chat.id)
            else AdminMessages.ADMIN_HELP
        ),
    )

    return


if __name__ == "__main__":
    print("/t--- Bot started ---")

    while True:
        time.sleep(10)

    exit()
