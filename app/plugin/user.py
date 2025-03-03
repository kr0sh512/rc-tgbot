from db import DB
from plugin.bot_instance import bot
from config import Messages
from telebot import types
from typing import List

users_reg: List["User"] = []


class User:
    _db = DB("Users")

    def __init__(self, user_id, name=None):
        self.user_id: int = user_id
        self._name: str = name
        self._age: int = None
        self._gender: str = None
        self._faculty: str = None
        self._group: str = None
        self._type: str = None

        self._load()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.update_data()

        return self._name

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = value
        self.update_data()

        return self._age

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, value):
        self._gender = value
        self.update_data()

        return self._gender

    @property
    def faculty(self):
        return self._faculty

    @faculty.setter
    def faculty(self, value):
        self._faculty = value
        self.update_data()

        return self._faculty

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        self._group = value
        self.update_data()

        return self._group

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value
        self.update_data()

        return self._type

    def _into_json(self):
        return {
            "_id": self.user_id,
            "name": self._name,
            "age": self._age,
            "gender": self._gender,
            "faculty": self._faculty,
            "group": self._group,
            "type": self._type,
        }

    def update_data(self):
        self._db.update({"_id": self.user_id}, self._into_json())

    def delete(self):
        self._db.delete({"_id": self.user_id})

    def get_all() -> list["User"]:
        users_data = User._db.find({})

        return [User(data["_id"]) for data in users_data]

    def _save(self):
        if not self._db.exist({"_id": self.user_id}):
            self._db.insert(self._into_json())
        else:
            self.update_data()

    def _load(self):
        if not self._db.exist({"_id": self.user_id}):
            self._save()
            # raise ValueError("User not found")

        data = self._db.find_one({"_id": self.user_id})
        self._name = data["name"]

        self._age = data["age"]
        self._gender = data["gender"]
        self._faculty = data["faculty"]
        self._group = data["group"]
        self._type = data["type"]

    @staticmethod
    def start_shuffle_reg():
        users_reg.clear()
        users = [user for user in User.get_all() if len(user.type) == 4]

        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Я тут!", callback_data="shuffle_agree"),
        )

        for user in users:
            bot.send_message(user.user_id, Messages.MATCHING_START, reply_markup=markup)

        return

    @staticmethod
    @bot.callback_query_handler(func=lambda call: call.data == "shuffle_agree")
    def add_user_to_reg(call: types.CallbackQuery):
        user = User(call.message.chat.id)
        users_reg.append(user)

        bot.edit_message_text(
            "Вы добавлены в список участников! Пожалуйста, подождите, пока все зарегистрируются",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None,
        )

        return

    def __str__(self):
        text = [f"{var}: {vars(self)[var]}" for var in vars(self) if var]
        text = "\n".join(text)

        return text
