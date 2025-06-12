import pytest
from app.models import UserBase


def test_user_creation():
    user = UserBase(
        first_name="Sasa",
        phone_number="22-33-22"
    )

    print(user)
    assert user.first_name == "Sasa"
    assert  user.phone_number == "22-33-22"