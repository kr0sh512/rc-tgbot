from db import DB
import config
from plugin.user import User
from plugin.shuffle import Shuffle

from plugin.bot_instance import bot

"""
логика: есть первый админ, который получается из config.ADMIN_ID все остальные админы добавляются только если есть свободная запись, сгенерированная другим админом - уникальный ключ. У админов есть свои команды для telebot, которые могут запускать только они
"""


class Admin:
    _db = DB("admins")

    def __init__(self, user_id):
        self.user_id = user_id
        self._load()

        return

    def _load(self):
        data = self._db.find_one({"user_id": self.user_id})
        if data:
            self.name = data["name"]
            self.added_by = data["added_by"]
        else:
            raise ValueError("Admin not found")

        return

    @staticmethod
    def is_admin(user_id):
        return Admin._db.find_one({"user_id": user_id}) is not None

    @staticmethod
    def add_admin(new_user_id, name, unique_key) -> int:
        key_data = Admin._db.find_one({"unique_key": unique_key})

        if new_user_id == config.ADMIN_ID and not Admin.is_admin(new_user_id):
            Admin._db.insert({"user_id": new_user_id, "name": name})

            return new_user_id

        if not key_data:
            raise ValueError("Unique key not found")

        if not Admin.is_admin(new_user_id):
            Admin._db.insert(
                {
                    "user_id": new_user_id,
                    "name": name,
                    "added_by": key_data["generated_by"],
                }
            )

            if key_data:
                Admin._db.delete({"unique_key": unique_key})

                return key_data["generated_by"]
        else:
            raise ValueError("Admin already exists")

        return

    @staticmethod
    def remove_admin(current_user_id, target_user_id):
        if target_user_id == config.ADMIN_ID:
            raise PermissionError("Cannot remove the first admin")

        if Admin.is_admin(current_user_id):
            if Admin.is_admin(target_user_id):
                Admin._db.delete({"user_id": target_user_id})
            else:
                raise ValueError("Admin not found")
        else:
            raise PermissionError("No permission to remove admin")

        return

    @staticmethod
    def generate_unique_key(admin_user_id):
        if Admin.is_admin(admin_user_id):
            import uuid

            unique_key = str(uuid.uuid4())
            while Admin._db.find_one({"unique_key": unique_key}):
                unique_key = str(uuid.uuid4())

            Admin._db.insert({"unique_key": unique_key, "generated_by": admin_user_id})

            return unique_key
        else:
            raise PermissionError("Only admins can generate unique keys")

        return

    # ----------------- TELEBOT ----------------- #

    def admin_only(func):
        def wrapper(message, *args, **kwargs):
            if Admin.is_admin(message.chat.id):
                return func(message, *args, **kwargs)
            else:
                bot.send_message(
                    message.chat.id, "У вас нет прав для выполнения этой команды."
                )

        return wrapper

    @bot.message_handler(commands=["admin"])
    def add_admin_command(message):
        bot.send_message(message.chat.id, "Введите unique_key")
        bot.register_next_step_handler(message, Admin.add_admin_step)

        return

    def add_admin_step(message):
        try:
            admin_id = Admin.add_admin(
                message.chat.id, message.from_user.username, message.text
            )
            bot.send_message(message.chat.id, "Вы добавлены в админы!")
            bot.send_message(
                admin_id,
                "По вашему ключу {} был добавлен новый админ {}".format(
                    message.text, message.from_user.username
                ),
            )
        except Exception as e:
            bot.send_message(message.chat.id, str(e))

        return

    @bot.message_handler(commands=["generate_key"])
    @admin_only
    def generate_key_command(message):
        try:
            key = Admin.generate_unique_key(message.chat.id)
            bot.send_message(
                message.chat.id,
                "Ваш ключ: <code>{}</code>".format(key),
                parse_mode="HTML",
            )
        except Exception as e:
            bot.send_message(message.chat.id, str(e))

        return

    @bot.message_handler(commands=["remove_admin"])
    @admin_only
    def remove_admin_command(message):
        bot.send_message(message.chat.id, "Введите user_id")
        bot.register_next_step_handler(message, Admin.remove_admin_step)

        return

    def remove_admin_step(message):
        try:
            Admin.remove_admin(message.chat.id, int(message.text))
            bot.send_message(message.chat.id, "Админ удален!")
        except Exception as e:
            bot.send_message(message.chat.id, str(e))

        return

    @bot.message_handler(commands=["delete_user"])
    @admin_only
    def delete_user_command(message):
        bot.send_message(message.chat.id, "Введите user_id")
        bot.register_next_step_handler(message, Admin.delete_user_step)

        return

    def delete_user_step(message):
        try:
            User(int(message.text)).delete()
            bot.send_message(message.chat.id, "Пользователь удален!")
        except Exception as e:
            bot.send_message(message.chat.id, str(e))

        return

    @bot.message_handler(commands=["stats"])
    @admin_only
    def stats_command(message):
        bot.send_message(message.chat.id, "Статистика")
        users = User.get_all()

        with open("stats.txt", "w") as f:
            f.write("Количество пользователей: {}\n".format(len(users)))

            for user in users:
                f.write(str(user) + "\n")

        with open("stats.txt", "rb") as f:
            bot.send_document(message.chat.id, f)

        with open("admin_stats.txt", "w") as f:
            admins = Admin._db.find({})
            f.write("Количество админов: {}\n".format(len(admins)))

            for admin in admins:
                f.write(str(admin) + "\n")

        with open("admin_stats.txt", "rb") as f:
            bot.send_document(message.chat.id, f)

        import os

        os.remove("stats.txt")
        os.remove("admin_stats.txt")

        return

    @bot.message_handler(commands=["send_message"])
    @admin_only
    def send_message_command(message):
        bot.send_message(
            message.chat.id, "Введите сообщение. Отправьте /cancel чтобы отменить"
        )
        bot.register_next_step_handler(message, Admin.send_message_step)

        return

    def send_message_step(message):
        if message.text == "/cancel":
            bot.send_message(message.chat.id, "Отменено")

            return

        users = User.get_all()
        for user in users:
            bot.send_message(user.user_id, message.text)

        bot.send_message(message.chat.id, "Сообщения отправлены!")

        return

    @bot.message_handler(commands=["clear_all"])
    @admin_only
    def clear_all_command(message):
        bot.send_message(
            message.chat.id,
            "Отправьте <code>delete all</code> для подтверждения",
            parse_mode="HTML",
        )

        return

    def clear_all_command_step(message):
        if message.text != "delete all":
            bot.send_message(message.chat.id, "Отменено")

        users = User.get_all()
        for user in users:
            user.delete()

        bot.send_message(message.chat.id, "Все пользователи удалены!")

        return

    @bot.message_handler(commands=["random"])
    @admin_only
    def random_command(message):
        users = User.get_all()
        Shuffle(users)

        return


class AdminMessages:
    ADMIN_HELP = (
        "Вы администратор! Вот что вы можете сделать:\n"
        "/remove_admin - удалить админа\n"
        "/generate_key - сгенерировать уникальный ключ"
        "/delete_user - удалить пользователя"
        "/stats - статистика"
        "/send_message - отправить всем сообщение"
        "/random - зарандомить людей для 1 тура"
        "clear_all - удаляет ВСЕХ пользователей"
    )
