import os
from typing import List
from datetime import datetime, timezone
from sqlmodel import SQLModel, create_engine, Session, select
from app.models import UserBase, User
from app.exceptions import UserNotFound
from app.logger import create_logger

# Extract the filename without extension
filename = os.path.splitext(os.path.basename(__file__))[0]

logger = create_logger(logger_name=__name__)


class DB:
    def __init__(self, db_file_name=""):
        if db_file_name == "":
            db_file_name = "database.db"
        self.engine = create_engine(f"sqlite:///{db_file_name}", echo=True)
        SQLModel.metadata.create_all(self.engine)

    def create_user(self, user: UserBase, session: Session) -> User:
        """
        Returns:
            created User
        """
        logger.info("Adding User")
        user_db = User.from_orm(user)
        session.add(user_db)
        session.commit()
        return user_db

    def get_user(self, user_id: int, session: Session) -> User:
        logger.info(f"Get User with ID {user_id} from DB")
        statement = select(User).where(User.id == user_id)
        result: User = session.exec(statement).first()
        if result:
            return result
        else:
            logger.error("User not found")
            raise UserNotFound(f"Не найден User с id {user_id}")

    # def delete_article(self, article_id: int, session: Session):
    #     logger.info(f"Удаление статьи с ID {article_id}")
    #     statement = select(Article).where(Article.id == article_id)
    #     article = session.exec(statement).one()
    #     session.delete(article)
    #     session.commit()
    #
    # def get_article_list(self, session: Session) -> List[Article]:
    #     logger.info("Reading all Articles from DB")
    #     statement = select(Article)
    #     results = session.exec(statement)
    #     return [r for r in results]
    #
    # def save_fragments(self, article: Article, fragments: list[FragmentBase], session: Session):
    #     if len(fragments) == 0:
    #         return
    #
    #     for fragment in fragments:
    #         fragment_db = Fragment.from_orm(fragment)
    #         fragment_db.article = article
    #         fragment_db.article_id = article.id
    #         session.add(fragment_db)
    #
    #     session.commit()
    #
    # def get_fragments(self, article_id:int, session: Session) -> List[Fragment]:
    #     logger.info("Reading fragments of Article from DB")
    #     statement = select(Fragment).where(Fragment.article_id == article_id)
    #     result = session.exec(statement).all()
    #     return [fr for fr in result]
    #
    # def in_vocab(self, word: str,  session: Session) -> bool:
    #     statement = select(Vocab).where(Vocab.word == word)
    #     result = session.exec(statement).all()
    #     return len(result) > 0
    #
    # def add_vocab(self, word: str, session: Session):
    #     if len(word) < 3:
    #         return
    #     if self.in_vocab(word, session):
    #         return
    #     item = Vocab()
    #     item.word = word
    #     session.add(item)
    #     session.commit()

sqlite_file_name = "database.db"
db = DB(sqlite_file_name)
