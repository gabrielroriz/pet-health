import pytest

from app.adapters.persistence.in_memory.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.in_memory.in_memory_token_service import InMemoryTokenService
from app.application.use_cases.auth.log_in import LogIn
from app.domain.errors import InvalidUserData


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def tokens() -> InMemoryTokenService:
    return InMemoryTokenService()


def test_creates_user_on_first_login(users, tokens):
    token = LogIn(users, tokens).execute("ana@example.com")

    user = users.get_by_email("ana@example.com")
    assert user is not None
    assert tokens.verify(token) == user.id


def test_reuses_user_with_same_email(users, tokens):
    log_in = LogIn(users, tokens)

    first = log_in.execute("ana@example.com")
    second = log_in.execute("  ANA@example.com ")

    assert len(users) == 1
    assert first != second
    assert tokens.verify(first) == tokens.verify(second)


def test_rejects_blank_email(users, tokens):
    with pytest.raises(InvalidUserData):
        LogIn(users, tokens).execute("  ")
