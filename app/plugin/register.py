from telebot import types
from plugin.user import User
from config import Messages
from plugin.test import TestMessages

from plugin.bot_instance import bot
import os
import re
import random


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
        types.InlineKeyboardButton("Согласен", callback_data="upload_agree"),
        types.InlineKeyboardButton("Не согласен", callback_data="upload_skip"),
    )
    bot.send_message(message.chat.id, Messages.ENTER_AGREE_UPLOAD, reply_markup=markup)

    return


@bot.callback_query_handler(func=lambda call: "upload" in call.data)
def start_agree_upload(call: types.CallbackQuery):
    user = User(call.message.chat.id)
    user.agree_upload = call.data.split("_")[-1] == "agree"

    bot.edit_message_text(
        (
            "Согласен на сохранение данных в общую базу"
            if user.agree_upload
            else "Не согласен на сохранение данных в общую базу"
        ),
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None,
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Всё верно!", callback_data="registration_confirm"),
        types.InlineKeyboardButton("Изменить", callback_data="registration_change"),
    )
    bot.send_message(
        call.message.chat.id,
        Messages.REGISTRATION_CONFIRM.format(
            user.name,
            user.age,
            "Парень" if user.gender == "man" else "Девушка",
            user.faculty,
            user.group,
            "Да" if user.agree_upload else "Нет",
        ),
        reply_markup=markup,
    )


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

    if call.data == "test_yes":
        last_q = -1
    else:
        last_q = int(call.data.split("_")[1].split("#")[0])
        previous_ans = int(call.data.split("#")[1])
        for ans_type in TestMessages.TEST_QUESTIONS[last_q]["answers"][previous_ans][
            "types"
        ]:
            add_score = 3 if last_q == 0 else 2
            user.vector_type[ans_type] = user.vector_type.get(ans_type, 0) + add_score

        prev_answ = "\n\n".join(
            [
                f"{'✅ ' if i == previous_ans else ''}{i+1}. {ans['text']}"
                for i, ans in enumerate(TestMessages.TEST_QUESTIONS[last_q]["answers"])
            ]
        )

        prev_text = f"{TestMessages.TEST_QUESTIONS[last_q]['question']}\n\n{prev_answ}"

        bot.edit_message_text(
            prev_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
        )

    if last_q == len(TestMessages.TEST_QUESTIONS) - 1:
        max_value = max(user.vector_type.values())
        max_types = [t for t, v in user.vector_type.items() if v == max_value]
        user.type = random.choice(max_types)

        show_result(call.message)
        return

    question = TestMessages.TEST_QUESTIONS[last_q + 1]
    answ = "\n\n".join(
        [f"{i+1}. {ans['text']}" for i, ans in enumerate(question["answers"])]
    )
    text = f"{question['question']}\n\n{answ}"

    markup = types.InlineKeyboardMarkup()
    for i in range(len(question["answers"])):
        markup.add(
            types.InlineKeyboardButton(
                f"{question['answers'][i]['short']}",
                callback_data=f"test_{last_q + 1}#{i}",
            )
        )

    bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")

    return


# @bot.callback_query_handler(func=lambda call: "test" in call.data)
# def test_question(call: types.CallbackQuery):
#     user = User(call.message.chat.id)

#     bot.edit_message_reply_markup(
#         call.message.chat.id, call.message.message_id, reply_markup=None
#     )

#     if call.data != "test_yes":
#         user.type += TestMessages.TEST_QUESTIONS[len(user.type)]["answers"][
#             int(call.data[-1])
#         ][1]

#         user_ans = int(call.data[-1])
#         question_last = TestMessages.TEST_QUESTIONS[len(user.type) - 1]
#         text_edit = f"{question_last['question']}\n\n{'✅ ' if user_ans == 0 else ''}1. {question_last['answers'][0][0]} \n\n{'✅ ' if user_ans == 1 else ''}2. {question_last['answers'][1][0]}"

#         bot.edit_message_text(
#             text_edit,
#             call.message.chat.id,
#             call.message.message_id,
#             parse_mode="HTML",
#         )  # упростить

#     if len(user.type) == 4:
#         show_result(call.message)
#         return

#     question = TestMessages.TEST_QUESTIONS[len(user.type)]
#     text = f"{question['question']}\n\n1. {question['answers'][0][0]} \n\n2. {question['answers'][1][0]}"
#     markup = types.InlineKeyboardMarkup()
#     markup.add(
#         types.InlineKeyboardButton("Первый вариант", callback_data=f"test_0"),
#         types.InlineKeyboardButton("Второй вариант", callback_data=f"test_1"),
#     )

#     bot.send_message(call.message.chat.id, text, reply_markup=markup)

#     return


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
