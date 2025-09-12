import sys
import json
import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove, ContentType

from sqlmodel import  Session

from app.bot.keyboards import kbs
from app.bot.utils.utils import greet_user, get_about_us_text
from app.models import User, UserBase #, TgUserMessageBase
from app.zulip_client import ZulipClient, ZulipException
#from app.bot.utils.rabbit_publisher import RabbitPublisher
from app.config import settings
from app.db import DB
from app.logger import create_logger


logger = create_logger(logger_name=__name__)
db = DB()
session = Session(db.engine)

user_router = Router()

try:
    zulip_client = ZulipClient()
except ZulipException:
    msg = "Фатальная ошибка при попытке коннекта к Zulip-серверу! Бот не запущен!"
    logger.critical(msg)
    sys.exit(msg)


def send_bot_event_msg_to_zulip(msg_text:str, topic='info'):
    zulip_client.send_msg_to_channel(
        channel_name="bot_events",
        topic=topic,
        msg=msg_text
    )


@user_router.message(Command("contact"))
async def share_number(message: Message):
    await message.answer(
        "Нажмите на кнопку ниже, чтобы отправить контакт",
        reply_markup=await kbs.contact_keyboard()
    )

# команда /start с доп.параметром  https://ru.stackoverflow.com/questions/1555324/
# в параметре можно передать, напр., ИД клиента
@user_router.message(CommandStart(deep_link=True))
async def cmd_start_with_param(message: Message, command: CommandObject):
    from_user = message.from_user
    msg_text = f"Команда /start от пользователя {from_user.first_name} с ID {from_user.id}"
    logger.info(msg_text)

    if command.args:
        # payload = decode_payload(command.args)
        payload = command.args
        send_bot_event_msg_to_zulip(f"{msg_text}. Доп.параметр: {payload}")

    await message.answer(get_about_us_text(), reply_markup=kbs.contact_keyboard())


@user_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    from_user = message.from_user
    msg_text = f"Команда /start от пользователя {from_user.first_name} с ID {from_user.id}"
    logger.info(msg_text)

    await message.answer(get_about_us_text(), reply_markup=kbs.contact_keyboard())


@user_router.message(F.contact)
async def get_contact(message: Message):
    contact = message.contact

    # клиент мог повторно отправить контакты, поэтому сначала ищем его в БД
    user_filter = {"tg_id": contact.user_id}
    user = db.get_user_one_or_none(user_filter, session)

    if not user:
        user = UserBase(
            first_name=contact.first_name,
            last_name=contact.last_name,
            phone_number=contact.phone_number,
            tg_id=contact.user_id
        )
        user = db.create_user(user, session)
        logger.info(f"Получены новые контакты: {user}. Польз.добавлен в БД.")

    msg_text = f"""Спасибо, {contact.first_name}.\n
        Ваш номер {contact.phone_number}, ваш ID {contact.user_id}.\n
        Теперь вы можете написать нам о своей проблеме."""

    zulip_client.send_msg_to_channel(
        channel_name="bot_events",
        topic="новый подписчик",
        msg=msg_text
    )

    # сначала channel_name = user.topic_name = [phone]_[tg_id]
    # после того как получис channel_id и сохраним его,
    # channel_name можно в Zulip переименовать вручную в понятное название клиента
    channel_name = user.topic_name

    if not user.zulip_channel_id:
        if not zulip_client.is_channel_exists(channel_name):
            # если в Zulip еще нет канала пользователя, то
            # - создаем канал, и подписываем на него всех сотрудников
            # - получаем его ID
            # - записываем ID в свойства user-а
            zulip_client.subscribe_to_channel(channel_name, settings.ZULIP_STAFF_IDS)
            channel_id = zulip_client.get_channel_id(channel_name)
            db.set_user_zulip_channel_id(user.id, channel_id, session)

            zulip_client.send_msg_to_channel(
                channel_name="bot_events",
                topic="новый подписчик",
                msg=f"Для пользователя {user} создан канал Zulip с id={channel_id}.",
            )
            logger.info(f"Для пользователя {user} создан канал Zulip с id={channel_id}.")


    await message.answer(
        msg_text,
        reply_markup=ReplyKeyboardRemove()
    )

# (F.from_user.id == 42) & (F.text == 'admin')
# F.text.startswith('a') | F.text.endswith('b')
@user_router.message((F.from_user.id == settings.ADMIN_ID) & F.text.startswith('//'))
async def admin_command(message: Message) -> None:
    """
    админская команда
    
    todo сделать проверки try...except..
    """
    cmd = message.text
    logger.info(f'Получена команда {cmd}')

    if '/list' in cmd:
        parts = cmd.split()
        try:
            from_id = int(parts[1])
        except IndexError:
            from_id = 0

        user_list = db.get_40_users_from_id(from_id, session)
        list_json = ''

        for user in user_list:
            list_json += user.model_dump_json()
            list_json += '\n'

        zulip_client.send_msg_to_channel(
            channel_name="bot_events",
            topic="ответы на команды",
            msg=list_json,
        )
        await message.answer('Команда /list обработана')
        logger.info('Команда /list обработана')

    elif '/upd' in cmd:
        parts = cmd.split()
        user_id = int(parts[1])
        update_data = json.loads(parts[2])
        db.update_user_from_dict(user_id, update_data, session)

        await message.answer(f"Запись пользователя {user_id} изменена")

    elif '/del' in cmd:
        parts = cmd.split()
        user_id = int(parts[1])
        user_str = db.delete_user(user_id, session)
        if user_str:
            await message.answer(f"{user_str} удален")
        else:
            await message.answer(f"Пользователь с id={user_id} не найден.")

    else:
        await message.answer(f"Неопознанная команда: {cmd}")



@user_router.message(F.text)
async def user_message(message: Message) -> None:
    """
    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """

    user_tg_id = message.from_user.id
    filter={"tg_id": user_tg_id}
    user = db.get_user_one_or_none(filter, session)

    if not user:
        await message.answer(
            "Вы еще не отправили ваш номер телефона.\n"
            "Нажмите на кнопку ОТПРАВИТЬ ниже.",
            reply_markup=kbs.contact_keyboard()
        )
        return

    logger.info(f"Получено сообщение от бота {message.text} от пользователя {user}")

    chat_type = message.chat.type
    topic_name = user.topic_name
    message_text = message.text
    if 'group' in chat_type:  # сообщение отправлено из группы
        topic_name = f"Группа_{message.chat.id}"
        message_text = f"{user.fio}: {message_text}"

    # отправим сообщение в Zulip
    zulip_client.send_msg_to_channel(user.zulip_channel_id, topic_name, message_text)

    await asyncio.sleep(0)


@user_router.message(F.photo)
async def get_photo(message: Message):
    user_tg_id = message.from_user.id
    filter={"tg_id": user_tg_id}
    user = db.get_user_one_or_none(filter, session)

    if not user:
        await message.answer(
            "Вы еще не отправили ваш номер телефона.\n"
            "Нажмите на кнопку ОТПРАВИТЬ ниже.",
            reply_markup=kbs.contact_keyboard()
        )
        return

    logger.info(f"Получено фото от пользователя {user}")

    largest_photo = message.photo[-1]
    if largest_photo.file_size > settings.MAX_FILE_SIZE * 1024 * 1024:
        await message.answer(
            "Очень большой размер фото.\n"
            "Макс допустимый размер - 20МБ."
        )
        return

    # фото сначала сохраняем на сервере бота
    destination = f"/tmp/{largest_photo.file_id}.jpg"
    await message.bot.download(file=largest_photo.file_id, destination=destination)

    #затем отправляем на сервер zulip
    with open(destination, "rb") as f:
        result = zulip_client.client.upload_file(f)

    #и отправим сообщение в Zulip с ссылкой на файл
    photo_url = f"{message.caption}\n[Фото]({result['url']})"
    zulip_client.send_msg_to_channel(user.zulip_channel_id, user.topic_name, photo_url)

    await asyncio.sleep(0)

