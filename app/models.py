from typing import Optional, List
import enum
from datetime import datetime, timezone

from sqlalchemy import String, Integer, table
from sqlalchemy.sql.schema import Column
from sqlmodel import Field, SQLModel, Relationship, Column, Enum


class UserType(str, enum.Enum):
    Staff = "staff"
    Client = "client"
    Anonim = "anonim"
    Admin = "admin"


class UserBase(SQLModel):
    first_name: str
    last_name: Optional[str] = Field(default=None, max_length=20)
    phone_number: str
    tg_id: Optional[int] = Field(default=None)
    zulip_channel_id: Optional[int] = Field(default=0)
    created_at: datetime = Field(
        default=datetime.now(timezone.utc),
        nullable=False,
    )
    user_type: UserType = Field(
        sa_column=Column(
            Enum(UserType),
            nullable=False,
            index=False
        ),
        default=UserType.Client,
    )
    pin_code: Optional[str] = Field(default=None, max_length=4)
    activated: bool = Field(default=False)

    @property
    def topic_name(self):
        return f"{self.fio}_{self.tg_id}"

    @property
    def fio(self):
        fio = self.first_name
        if self.last_name:
            fio += f" {self.last_name}"
        return fio

    def update_from_dict(self, update_data:dict):
        for attr_name, attr_value in update_data.items():
            #attr = self.__getattr__(attr_name)
            self.__setattr__(attr_name, attr_value)

    def __str__(self):
        return f"{self.fio}, тел:{self.phone_number}, tg_id:{self.tg_id}"


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str = Field(sa_column=Column("phone_number", String, unique=True))
    #tg_messages: List["TgUserMessage"] = Relationship(back_populates="user", cascade_delete=False)


# class TgUserMessageBase(SQLModel):
#     from_u_id: int
#     from_u_tg_id: int
#     to_u_id: Optional[int] = Field(default=None)
#     sent_at: datetime = Field(
#         default=datetime.now(timezone.utc),
#         nullable=False,
#         description="Когда сообщение отправлено",
#     )
#     read: bool = Field(default=False)
#     read_at: Optional[datetime] = Field(
#         default=None,
#         #nullable=False,
#         description="Когда сообщение прочитано",
#     )
#     text: str
#
# class TgUserMessage(TgUserMessageBase, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     from_u_id: int = Field(default=None, foreign_key="user.id", ondelete="RESTRICT")
#     user: User = Relationship(back_populates="tg_messages")
#
#

# class FragmentBase(SQLModel):
#     text: str
#
#     def lemmatize(self):
#         doc = nlp(self.text)
#         lemmas = [token.lemma_ for token in doc]
#         lemmas = remove_punctuations(lemmas)
#         #print(lemmas)
#         return lemmas
#
#
# class Fragment(FragmentBase, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     article_id: int = Field(default=None, foreign_key="article.id", ondelete="CASCADE")
#     article: Article = Relationship(back_populates="fragments")
#
#
# class Vocab(SQLModel, table=True):
#     word: str = Field(primary_key=True)


"""  Согласие на обработку ПД
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ... (импорт и инициализация бота)

async def cmd_start(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup()
    agree_button = InlineKeyboardButton(text="Согласен", callback_data="agree_pdn")
    disagree_button = InlineKeyboardButton(text="Отказаться", callback_data="disagree_pdn")
    keyboard.add(agree_button, disagree_button)
    
    await message.answer(
        "Привет! Я бот [Название]. Для продолжения работы мне нужно ваше согласие на обработку персональных данных. Подробнее в <a href='ссылка_на_политику'>Политике конфиденциальности</a>.",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

async def process_callback_pdn(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "agree_pdn":
        user_id = callback_query.from_user.id
        # Сохраняем факт согласия в БД
        # await save_user_consent(user_id) 
        await callback_query.message.answer("Спасибо! Вы дали согласие. Теперь вы можете пользоваться ботом.")
        await state.finish() # Или переход в другое состояние
    elif callback_query.data == "disagree_pdn":
        await callback_query.message.answer("Вы отказались от обработки ПДн. Бот не сможет продолжить работу.")
        await callback_query.message.delete() # Удаляем кнопки
"""