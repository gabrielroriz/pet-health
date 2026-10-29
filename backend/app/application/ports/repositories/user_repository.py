from typing import Protocol
from uuid import UUID

from app.domain.user import User


# What the auth use cases need from storage; the adapters in persistence/ implement it.
class UserRepository(Protocol):
    def add(self, user: User) -> None: ...

    def get(self, user_id: UUID) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...
