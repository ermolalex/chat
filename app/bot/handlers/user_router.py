import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
#from app.api.dao import UserDAO
from app.bot.keyboards import kbs
from app.bot.utils.utils import greet_user, get_about_us_text

user_router = Router()


@user_router.message(Command("contact"))
async def share_number(message: Message):
    await message.answer(
        "Нажмите на кнопку ниже, чтобы отправить контакт",
        reply_markup=await kbs.contact_keyboard()
    )

@user_router.message(ContentType.CONTACT) #content_types=ContentType.CONTACT)
async def get_contact(message: Message):
    contact = message.contact
    await message.answer(f"Спасибо, {contact.full_name}.\n"
                         f"Ваш номер {contact.phone_number} был получен",
                         reply_markup=ReplyKeyboardRemove())


@user_router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    logging.info("SОбрабатываем команду /start.")
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
    await message.answer(get_about_us_text()) #, reply_markup=kb)
    # await greet_user(message) #, is_new_user=not user)
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
