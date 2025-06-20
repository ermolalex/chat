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

    def __str__(self):
        return f"{self.fio}, тел:{self.phone_number}, tg_id:{self.tg_id}"


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str = Field(sa_column=Column("phone_number", String, unique=True))
    tg_messages: List["TgUserMessage"] = Relationship(back_populates="user", cascade_delete=False)


class TgUserMessageBase(SQLModel):
    from_u_id: int
    from_u_tg_id: int
    to_u_id: Optional[int] = Field(default=None)
    sent_at: datetime = Field(
        default=datetime.now(timezone.utc),
        nullable=False,
        description="Когда сообщение отправлено",
    )
    read: bool = Field(default=False)
    read_at: Optional[datetime] = Field(
        default=None,
        #nullable=False,
        description="Когда сообщение прочитано",
    )
    text: str

class TgUserMessage(TgUserMessageBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_u_id: int = Field(default=None, foreign_key="user.id", ondelete="RESTRICT")
    user: User = Relationship(back_populates="tg_messages")



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