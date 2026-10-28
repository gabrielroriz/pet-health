from uuid import uuid4

import pytest

from app.adapters.persistence.in_memory.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.in_memory.in_memory_token_service import InMemoryTokenService
from app.application.use_cases.auth.authenticate import Authenticate
from app.domain.errors import NotAuthenticated
from app.domain.user import User


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def tokens() -> InMemoryTokenService:
    return InMemoryTokenService()


def test_returns_user_for_valid_token(users, tokens):
    user = User(email="ana@example.com")
    users.add(user)

    assert Authenticate(users, tokens).execute(tokens.issue(user.id)) is user


def test_rejects_unknown_token(users, tokens):
    with pytest.raises(NotAuthenticated):
        Authenticate(users, tokens).execute("unknown-token")


def test_rejects_token_of_missing_user(users, tokens):
    with pytest.raises(NotAuthenticated):
        Authenticate(users, tokens).execute(tokens.issue(uuid4()))
