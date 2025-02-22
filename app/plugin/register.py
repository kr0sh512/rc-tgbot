import telebot
from telebot import types
from plugin.user import User
from config import Messages
from plugin.test import TestMessages

from plugin.bot_instance import bot


def start_reg_name(message: types.Message):
    user = User(message.chat.id, message.text)

    bot.send_message(message.chat.id, Messages.ENTER_AGE)

    bot.register_next_step_handler(message, start_reg_age)


def start_reg_age(message: types.Message):
    user = User(message.chat.id)
    user.age = int(message.text)

    markup = types.InlineKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.InlineKeyboardButton(Messages.GENDER_WOMAN, callback_data="gender_woman"),
        types.InlineKeyboardButton(Messages.GENDER_MAN, callback_data="gender_man"),
    )
    bot.send_message(message.chat.id, Messages.ENTER_GENDER)

    bot.register_next_step_handler(message, start_reg_gender)


@bot.callback_query_handler(func=lambda call: "gender" in call.data)
def start_reg_gender(call: types.CallbackQuery):
    user = User(call.message.chat.id)
    user.gender = call.data.split("_")[-1]

    bot.edit_message_text(
        Messages.GENDER_WOMAN if user.gender == "woman" else Messages.GENDER_MAN,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None,
    )

    bot.send_message(call.message.chat.id, Messages.ENTER_FACULTY)

    bot.register_next_step_handler(call.message, start_reg_faculty)


def start_reg_faculty(message: types.Message):
    user = User(message.chat.id)
    user.faculty = message.text

    bot.send_message(message.chat.id, Messages.ENTER_GROUP)

    bot.register_next_step_handler(message, start_reg_group)


def start_reg_group(message: types.Message):
    user = User(message.chat.id)
    user.group = message.text

    markup = types.InlineKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.InlineKeyboardButton("Всё верно!", callback_data="registration_confirm"),
        types.InlineKeyboardButton("Изменить", callback_data="registration_change"),
    )
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


@bot.callback_query_handler(func=lambda call: call.data == "registration_skip")
def start_skip_reg(call: types.CallbackQuery):
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id, reply_markup=None
    )

    return


@bot.callback_query_handler(func=lambda call: call.data == "registration_change")
def start_reg_again(call: types.CallbackQuery):
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id, reply_markup=None
    )

    bot.send_message(call.message.chat.id, Messages.ENTER_NAME)

    bot.register_next_step_handler(call.message, start_reg_name)


@bot.callback_query_handler(func=lambda call: call.data == "registration_confirm")
def start_test(call: types.CallbackQuery):
    user = User(call.message.chat.id)
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id, reply_markup=None
    )

    bot.send_message(call.message.chat.id, TestMessages.TEST_WELCOME)

    pass
