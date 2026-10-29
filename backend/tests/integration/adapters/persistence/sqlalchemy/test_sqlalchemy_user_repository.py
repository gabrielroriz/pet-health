import pytest
from sqlalchemy.exc import IntegrityError

from app.adapters.persistence.sqlalchemy.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.domain.user import User


def test_gets_added_user_by_id_and_email(session):
    users = SqlAlchemyUserRepository(session)
    user = User(email="ana@example.com")

    users.add(user)

    assert users.get(user.id) == user
    assert users.get_by_email("ana@example.com") == user
    assert users.get_by_email("bob@example.com") is None


def test_database_rejects_duplicate_email(session):
    users = SqlAlchemyUserRepository(session)
    users.add(User(email="ana@example.com"))

    with pytest.raises(IntegrityError):
        users.add(User(email="ana@example.com"))
