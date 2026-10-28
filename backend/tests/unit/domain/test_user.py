import pytest

from app.domain.errors import InvalidUserData
from app.domain.user import User


def test_normalizes_email():
    assert User(email="  Ana@Example.COM ").email == "ana@example.com"


@pytest.mark.parametrize("email", ["", "   "])
def test_rejects_blank_email(email):
    with pytest.raises(InvalidUserData):
        User(email=email)
