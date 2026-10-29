from typing import Protocol
from uuid import UUID

from app.domain.pet import Pet


# What the pet use cases need from storage; the adapters in persistence/ implement it.
class PetRepository(Protocol):
    def add(self, pet: Pet) -> None: ...

    def get(self, pet_id: UUID) -> Pet | None: ...

    def list_by_owner(self, owner_id: UUID) -> list[Pet]: ...
