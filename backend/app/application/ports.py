from typing import Protocol
from uuid import UUID

from app.domain.pet import Pet


class PetRepository(Protocol):
    def add(self, pet: Pet) -> None: ...

    def get(self, pet_id: UUID) -> Pet | None: ...
