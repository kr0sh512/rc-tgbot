# Бот Random Coffe для Telegram

Бот реализован с помощью библиотеки [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/) и базы данных [MongoDB](https://www.mongodb.com/)

## Запуск

1. Создать [файл .env](#env) в директории `app`
2. Запустить контейнеры с помощью docker compose:
   - `docker-compose up -d`

Без контейнеров:

1. Установка нужных модулей
   - `pip3 install -r app/requirements.txt`
2. Запуск скрипта:
   - `(cd ./app && python3 main.py)`

## Функционал

1. Регистрация участников с мини-тестом для определения типа личности
2. Генерация пар для рассадки людей по:
   1. М+Ж по MBTI
   2. М+Ж
   3. одного возраста
   4. всех остальных
3. Возможность уведомлять всех пользователей
4. Поддержка нескольких администраторов
5. Отправка за день уведомления о начале мероприятия

## Команды

### Пользователи

- Вначале пользователям предоставляется небольшая регистрация после `/start`
- Довольно бесполезный `/help`
- Исходный код на Github `/source`

### Администраторы

- `/generate_key` - создание уникального ключа для добавления новых админов
- `/admin_reg` - добавиться в админы (с последующим вводом unique_key)
- `/stats` - получить информацию о пользователях
- `/delete_user` - удалить пользователя по id
- `/send_message` - сделать массовую рассылку всем зарегестрированным пользователям
- `/random` - запустить рассылку для регистрации на первый тур
- `/random_again` - сгенерировать повторную рассадку для людей первого тура (без повторной регистрации)
- `/clear_all` - удалить всех людей из базы данных
- `/remove_admin` - удалить админа по id
- `/restart` - перезапуск бота (только для Docker запуска)

## <a id="env">Настройка конфигурации</a>

Необходимые поля в `.env` файле:

- `DATE_START` в формате `%Y-%m-%d`
- `TIME_START` в формате `%HH-%MM`
- `API_TOKEN` - токен для tg бота полученный у `@BotFather`
- `ADMIN_ID` - id **_главного админа_**
- `DB_PORT` порт для MongoDB, стандартно `27017`
- `ENV` - если выставлен как `dev`:
  - возможность подключаться к базе данных удалённо через SSH
  - `SSH_HOST` - имя/ip хоста
  - `SSH_USER` - имя пользователя
  - `SSH_KEY` - расположение ключа (может быть не указан если есть `SSH_PASSWORD`)
  - `SSH_PASSWORD` - пароль порльзователя (может быть не указан если есть `SSH_KEY`)
