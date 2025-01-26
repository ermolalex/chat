import pytest
from sqlmodel import Session
from app.db import DB
from app.models import UserBase


@pytest.fixture
def user1():
    user = UserBase(
        first_name="Sasa",
        last_name="Erm",
        phone_number="22-33-22",
        tg_id=123,
    )
    yield user


@pytest.fixture
def user2():
    user = UserBase(
        first_name="Masa",
        phone_number="11-33-22",
    )
    yield user


@pytest.fixture
def db_instance(scope="session"):
    db = DB("test.db")
    yield db


@pytest.fixture
def session(db_instance, scope="session"):
    session = Session(db_instance.engine)
    yield session
    session.close()


@pytest.fixture
def db_instance_empty(db_instance, session, scope="function"):
    # Clear DB before test function
    db_instance.delete_all_users(session=session)
    yield db_instance

    # Clear DB after test function
    db_instance.delete_all_users(session=session)
