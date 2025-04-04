import asyncio
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
from app.bot.keyboards import kbs
from app.bot.utils.utils import greet_user, get_about_us_text
from app.models import User, UserBase, TgUserMessageBase
from app.bot.utils.rabbit_publisher import RabbitPublisher
from app.config import settings

from app.db import DB
from sqlmodel import  Session


db = DB()
session = Session(db.engine)

user_router = Router()

rabbit_publisher = RabbitPublisher()


@user_router.message(Command("contact"))
async def share_number(message: Message):
    await message.answer(
        "Нажмите на кнопку ниже, чтобы отправить контакт",
        reply_markup=await kbs.contact_keyboard()
    )

@user_router.message(F.contact) #ContentType.CONTACT) #content_types=ContentType.CONTACT)
async def get_contact(message: Message):
    contact = message.contact

    user = UserBase(
        first_name=contact.first_name,
        last_name=contact.last_name,
        phone_number=contact.phone_number,
        tg_id=contact.user_id
    )
    db.create_user(user, session)

    await message.answer(f"Спасибо, {contact.first_name}.\n"
                         f"Ваш номер {contact.phone_number}, ваш ID {contact.user_id}.\n"
                         f"Теперь вы можете написать нам о своей проблеме.",
                         reply_markup=ReplyKeyboardRemove())


@user_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    logging.info(f"Обрабатываем команду /start от пользователя с id={user_id}")
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

    # logging.info(f"Получено сообщение {message.text} от пользователя {user}")
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

    rabbit_publisher.publish(
        message.text,
        {
            'user_name': user.first_name,
            'user_phone': user.phone_number,
            'user_tg_id': user.tg_id,
        }
    )

    await asyncio.sleep(0)
    #await message.answer("")

    # try:
    #     # Send a copy of the received message
    #     await message.send_copy(chat_id=message.chat.id)
    # except TypeError:
    #     # But not all the types is supported to be copied so need to handle it
    #     await message.answer("Nice try!")

#
# @user_router.message(F.text == '🔙 Назад')
# async def cmd_back_home(message: Message) -> None:
#     """
#     Обрабатывает нажатие кнопки "Назад".
#     """
#     await greet_user(message, is_new_user=False)
#
# @user_router.message(F.text == "ℹ️ О нас")
# async def about_us(message: Message):
#     #kb = app_keyboard(user_id=message.from_user.id, first_name=message.from_user.first_name)
#     # await message.answer(get_about_us_text(), reply_markup=kb)
#     await message.answer(get_about_us_text())