from app.adapters.persistence.in_memory.in_memory_user_repository import InMemoryUserRepository
from app.domain.user import User


def test_gets_added_user_by_id_and_email():
    users = InMemoryUserRepository()
    user = User(email="ana@example.com")

    users.add(user)

    assert users.get(user.id) is user
    assert users.get_by_email("ana@example.com") is user
    assert users.get_by_email("bob@example.com") is None
