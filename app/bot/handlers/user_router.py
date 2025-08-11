import sys
import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
from sqlmodel import  Session

from app.bot.keyboards import kbs
from app.bot.utils.utils import greet_user, get_about_us_text
from app.models import User, UserBase, TgUserMessageBase
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


#rabbit_publisher = RabbitPublisher()

@user_router.message(Command("contact"))
async def share_number(message: Message):
    await message.answer(
        "Нажмите на кнопку ниже, чтобы отправить контакт",
        reply_markup=await kbs.contact_keyboard()
    )


@user_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    logger.info(f"Обрабатываем команду /start от пользователя с id={user_id}")
    """
    Обрабатывает команду /start.
    user = await UserDAO.find_one_or_none(telegram_id=message.from_user.id)

    if not user:
        await UserDAO.add(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            username=message.from_user.username
        )

    """
    await message.answer(get_about_us_text(), reply_markup=kbs.contact_keyboard())
    # await greet_user(message) #, is_new_user=not user)


@user_router.message(F.contact) #ContentType.CONTACT) #content_types=ContentType.CONTACT)
async def get_contact(message: Message):
    contact = message.contact

    user = UserBase(
        first_name=contact.first_name,
        last_name=contact.last_name,
        phone_number=contact.phone_number,
        tg_id=contact.user_id
    )
    user_db = db.create_user(user, session)
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
            db.set_user_zulip_channel_id(user_db.id, channel_id, session)

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
@user_router.message((F.from_user.id == settings.ADMIN_ID) & F.text.startswith('/'))
async def admin_command(message: Message) -> None:
    """
    админская команда
    """
    user_tg_id = message.from_user.id
    text = f"Получена команда: {message.text}"

    await message.answer(
        text
    )



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
    # if not user.activated:
    #     await message.answer("Учетка не активирована")
    #     return

    # сохраним сообщение в БД todo
    tg_message = TgUserMessageBase(
        from_u_id=user.id,
        from_u_tg_id=user.tg_id,
        text=message.text
    )
    db.add_tg_message(tg_message, session)

    # отправим сообщение в Zulip
    zulip_client.send_msg_to_channel(user.zulip_channel_id, user.topic_name, message.text)

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

    # фото сначала сохраняем на сервере бота
    destination = f"/tmp/{message.photo[-1].file_id}.jpg"
    await message.bot.download(file=message.photo[-1].file_id, destination=destination)

    #затем отправляем на сервер zulip
    with open(destination, "rb") as f:
        result = zulip_client.client.upload_file(f)

    #и отправим сообщение в Zulip с ссылкой на файл
    photo_url = f"{message.caption}\n[Фото]({result['url']})"
    zulip_client.send_msg_to_channel(user.zulip_channel_id, user.topic_name, photo_url)

    await asyncio.sleep(0)

