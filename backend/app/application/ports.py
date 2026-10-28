from typing import Protocol
from uuid import UUID

from app.domain.pet import Pet
from app.domain.user import User


class PetRepository(Protocol):
    def add(self, pet: Pet) -> None: ...

    def get(self, pet_id: UUID) -> Pet | None: ...


class UserRepository(Protocol):
    def add(self, user: User) -> None: ...

    def get(self, user_id: UUID) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...


class TokenService(Protocol):
    def issue(self, user_id: UUID) -> str: ...

    def verify(self, token: str) -> UUID | None: ...
