from telebot import types
from plugin.user import User
from config import Messages
from plugin.test import TestMessages

from plugin.bot_instance import bot
import os
import re


def start_reg_name(message: types.Message):
    user = User(message.chat.id)
    user.name = message.text

    bot.send_message(message.chat.id, Messages.ENTER_AGE)

    bot.register_next_step_handler(message, start_reg_age)

    return


def start_reg_age(message: types.Message):
    user = User(message.chat.id)

    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Введите число")

        bot.register_next_step_handler(message, start_reg_age)

        return

    user.age = int(message.text)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(Messages.GENDER_WOMAN, callback_data="gender_woman"),
        types.InlineKeyboardButton(Messages.GENDER_MAN, callback_data="gender_man"),
    )
    bot.send_message(message.chat.id, Messages.ENTER_GENDER, reply_markup=markup)

    return


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

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Всё верно!", callback_data="registration_confirm"),
        types.InlineKeyboardButton("Изменить", callback_data="registration_change"),
    )
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


# --------------------------------- Test ---------------------------------


@bot.callback_query_handler(func=lambda call: call.data == "registration_confirm")
def start_test(call: types.CallbackQuery):
    user = User(call.message.chat.id)
    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id, reply_markup=None
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Начнём!", callback_data="test_yes"),
    )
    bot.send_message(
        call.message.chat.id, TestMessages.TEST_WELCOME, reply_markup=markup
    )
    user.type = ""

    return


@bot.callback_query_handler(func=lambda call: "test" in call.data)
def test_question(call: types.CallbackQuery):
    user = User(call.message.chat.id)

    bot.edit_message_reply_markup(
        call.message.chat.id, call.message.message_id, reply_markup=None
    )

    if call.data != "test_yes":
        user.type += TestMessages.TEST_QUESTIONS[len(user.type)]["answers"][
            int(call.data[-1])
        ][1]

        user_ans = int(call.data[-1])
        question_last = TestMessages.TEST_QUESTIONS[len(user.type) - 1]
        text_edit = f"{question_last['question']}\n\n{"✅ " if user_ans == 0 else ""}1. {question_last['answers'][0][0]} \n\n{"✅ " if user_ans == 1 else ""}2. {question_last['answers'][1][0]}"

        bot.edit_message_text(
            text_edit,
            call.message.chat.id,
            call.message.message_id,
        )  # упростить

    if len(user.type) == 4:
        show_result(call.message)
        return

    question = TestMessages.TEST_QUESTIONS[len(user.type)]
    text = f"{question['question']}\n\n1. {question['answers'][0][0]} \n\n2. {question['answers'][1][0]}"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Первый вариант", callback_data=f"test_0"),
        types.InlineKeyboardButton("Второй вариант", callback_data=f"test_1"),
    )

    bot.send_message(call.message.chat.id, text, reply_markup=markup)

    return


def show_result(message: types.Message):
    user = User(message.chat.id)
    text = TestMessages.TEST_RESULT.format(
        TestMessages.TEST_RESULTS[user.type][0],
        TestMessages.TEST_RESULTS[user.type][1],
    )

    directory = "pics/"
    pattern = re.compile(f"{user.type}.*\.(jpg|jpeg|png|gif)$", re.IGNORECASE)

    image_path = None
    for filename in os.listdir(directory):
        if pattern.match(filename):
            image_path = os.path.join(directory, filename)
            break

    if image_path:
        bot.send_photo(
            message.chat.id,
            open(image_path, "rb"),
            caption=text,
            show_caption_above_media=True,
        )
    else:
        print("Image not found")

    bot.send_message(message.chat.id, TestMessages.TEST_FINISH)
    bot.send_message(message.chat.id, Messages.START_DATE)

    return
