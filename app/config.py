import os
from datetime import datetime
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv

load_dotenv()


class config:
    DATE_START = datetime.strptime(
        f'{os.environ.get("DATE_START")}-{os.environ.get("TIME_START")}',
        "%Y-%m-%d-%H:%M",
    )
    API_TOKEN = os.environ.get("API_TOKEN")
    ADMIN_ID = int(os.environ.get("ADMIN_ID"))
    ENV = os.getenv("ENV", "PROD")

    DB_PORT = int(os.getenv("DB_PORT", 27017))
    if ENV == "DEV":
        server = SSHTunnelForwarder(
            (os.environ.get("SSH_HOST"), 22),
            ssh_private_key=os.getenv("SSH_KEY", None),
            ssh_username=os.environ.get("SSH_USER"),
            ssh_password=os.getenv("SSH_PASSWORD", None),
            remote_bind_address=("localhost", DB_PORT),
        )
        server.start()

        DB_PORT = server.local_bind_port


class Messages:
    WELCOME_LIST = [
        (
            "Привет! Это бот <b>Random Coffee</b>."
            "\n\nЧтобы зарегистрироваться, ответь на следующие вопросы ⬇️"
        )  # несколько сообщений подряд
    ]
    HELPS = [
        (
            "Доступные команды:"
            "\n/start - начать регистрацию"
            "\n/help - помощь"
            "\n/source - исходный код бота на Github"
            "\n\nCreated by АйТи блок ВМК with love ❤️"
        )
    ]

    ERROR = "Произошла ошибка"
    ENTER_NAME = "Как тебя зовут?"
    ENTER_AGE = "Сколько тебе лет?"
    ENTER_GENDER = "Выбери пол"
    GENDER_WOMAN = "Я девушка"  # кнопки выбора
    GENDER_MAN = "Я парень"  # кнопки выбора
    ENTER_FACULTY = "С какого ты факультета?"
    ENTER_GROUP = "Напиши номер своей группы"
    ENTER_AGREE_UPLOAD = (
        "Согласен ли ты на сохранение своих данных в общую базу для подбора пар?"
    )
    REGISTRATION_CONFIRM = "<u>Твои данные:</u>\
        \n\n<b>Имя:</b> {}\
        \n<b>Возраст:</b> {}\
        \n<b>Пол:</b> {}\
        \n<b>Факультет:</b> {}\
        \n<b>Группа:</b> {}\
        \n<b>Согласие на сохранение данных:</b> {}\
        \n\nВсё верно?"
    ALREADY_REGISTERED = "Ты уже зарегистрирован. Хочешь изменить данные?"
    MATCHING_START = (
        "Мы начали подбор пар 🤩" "\nПодтверди своё нахождение в аудитории."
    )
    START_DATE = (
        "Мероприятие начнётся:"
        "\n🗓️ <b>3 апреля в 18:00</b>"
        "\n\nСледите за новостями!"
    )
