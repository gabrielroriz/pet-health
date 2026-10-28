from uuid import UUID

from app.domain.pet import Pet
from app.domain.user import User


class InMemoryPetRepository:
    def __init__(self) -> None:
        self._pets: dict[UUID, Pet] = {}

    def __len__(self) -> int:
        return len(self._pets)

    def add(self, pet: Pet) -> None:
        self._pets[pet.id] = pet

    def get(self, pet_id: UUID) -> Pet | None:
        return self._pets.get(pet_id)


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
        return next((u for u in self._users.values() if u.email == email), None)
