import os
from typing import List
from datetime import datetime, timezone
from sqlalchemy import exc
from sqlmodel import SQLModel, create_engine, Session, select, delete
from app.models import UserBase, User, TgUserMessageBase, TgUserMessage
from app.exceptions import UserNotFound, UserPhoneNumberAlreadyExists
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
        user_db = User.from_orm(user)
        try:
            session.add(user_db)
            session.commit()
            session.refresh(user_db)
            logger.info(f"Добавлен Клиент {user}.")
        except exc.IntegrityError:
            logger.info(f"Клиент с номером телефона {user.phone_number} уже существует")
            session.rollback()
            user_db = None
        except Exception as e:
            logger.info(f"Не удалось добавить Клиента {user} - {e}")
            session.rollback()
            user_db = None
        return user_db

    def get_user_by_id(self, user_id: int, session: Session) -> User:
        logger.info(f"Get User with ID {user_id} from DB")
        statement = select(User).where(User.id == user_id)
        result: User = session.exec(statement).one_or_none()
        if result:
            return result
        else:
            logger.error("User not found")
            raise UserNotFound(f"Не найден User с id {user_id}")

    def get_user_one_or_none(self, filter: dict, session: Session):
        logger.info(f"Поиск Пользователя по фильтру: {filter}")

        if "id" in filter.keys():
            statement = select(User).where(User.id == filter["id"])
        elif "phone_number" in filter.keys():
            statement = select(User).where(User.phone_number == filter["phone_number"])
        elif "tg_id" in filter.keys():
            statement = select(User).where(User.tg_id == filter["tg_id"])
        elif "first_name" in filter.keys():
            statement = select(User).where(User.first_name == filter["first_name"])
        else:
            raise UserNotFound(f"Некорректный фильтр для поиска пользователя - {filter}")

        try:
            result: User = session.exec(statement).one_or_none()

            log_message = f"Пользователь {'найден' if result else 'не найден'}"
            logger.info(log_message)
            return result
        except exc.SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске Пользователя по фильтрам {filters}: {e}")
            raise


    def get_user_by_phone_number(self, phone_number: str, session: Session) -> User:
        logger.info(f"Get User by phone_number {phone_number}")
        statement = select(User).where(User.phone_number == phone_number)
        result: User = session.exec(statement).first()
        if result:
            return result
        else:
            logger.error("User not found")
            raise UserNotFound(f"Не найден User с номером телефона {phone_number}")

    def delete_all_users(self, session: Session):
        logger.info(f"Удаление всех  User'ов")
        statement = delete(User)
        result = session.exec(statement)
        session.commit()
        logger.info(f"Удаление всех  User'ов. (result.rowcount={result.rowcount})")

    def add_tg_message(self, message: TgUserMessageBase, session: Session):
        message_db = TgUserMessage.from_orm(message)
        try:
            session.add(message_db)
            session.commit()
            session.refresh(message_db)
            logger.info(f"Добавлено сообщение от {message_db.user.first_name}: {message_db.text[:20]}...")
        except Exception as e:
            logger.info(f"Ошибка при сохранения сообщения {message_db}...")
            session.rollback()
            raise
        return #user_db

    def get_messages(self, session: Session) -> List[TgUserMessage]:
        logger.info("Читаем все сообщения из БД")
        statement = select(TgUserMessage)
        results = session.exec(statement)
        return [r for r in results]


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
#db = DB(sqlite_file_name)