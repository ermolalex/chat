from typing import Optional, List
import enum
from datetime import datetime, timezone

from sqlalchemy import String, Integer
from sqlalchemy.sql.schema import Column
from sqlmodel import Field, SQLModel, Relationship, Column, Enum


class ArticleType(str, enum.Enum):
    Pdf = "pdf"
    Plain = "plain"
    Url = "url"


class UserBase(SQLModel):
    first_name: str
    last_name: Optional[str] = Field(default=None, max_length=20)
    phone_number: str
    tg_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(
        default=datetime.now(timezone.utc),
        nullable=False,
        description="The timestamp of when the task was created",
    )
    # article_type: ArticleType = Field(
    #     sa_column=Column(
    #         Enum(ArticleType),
    #         nullable=False,
    #         index=False
    #     ),
    #     default=ArticleType.Plain,
    # )
    # url: Optional[str] = Field(default="")
    # text: Optional[str] = Field(default="")


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    phone_number: str = Field(sa_column=Column("phone_number", String, unique=True))
    # fragments: List["Fragment"] = Relationship(back_populates="article", cascade_delete=True)


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
