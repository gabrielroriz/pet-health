from uuid import UUID

from app.domain.user import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    def __len__(self) -> int:
        return len(self._users)

    def add(self, user: User) -> None:
        self._users[user.id] = user

    def get(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        # Emails are already normalized by User, so a plain comparison is enough.
        return next((u for u in self._users.values() if u.email == email), None)
