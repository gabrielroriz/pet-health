from uuid import uuid4

from app.adapters.security.in_memory.in_memory_token_service import InMemoryTokenService


def test_verifies_issued_token():
    tokens = InMemoryTokenService()
    user_id = uuid4()

    assert tokens.verify(tokens.issue(user_id)) == user_id


def test_issues_unique_tokens():
    tokens = InMemoryTokenService()
    user_id = uuid4()

    assert tokens.issue(user_id) != tokens.issue(user_id)


def test_rejects_unknown_token():
    assert InMemoryTokenService().verify("unknown-token") is None
