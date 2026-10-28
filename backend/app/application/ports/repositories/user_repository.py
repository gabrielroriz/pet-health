from typing import Protocol
from uuid import UUID

from app.domain.user import User


class UserRepository(Protocol):
    def add(self, user: User) -> None: ...

    def get(self, user_id: UUID) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...
