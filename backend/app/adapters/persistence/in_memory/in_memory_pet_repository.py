from uuid import UUID

from app.domain.pet import Pet


class InMemoryPetRepository:
    def __init__(self) -> None:
        self._pets: dict[UUID, Pet] = {}

    def __len__(self) -> int:
        return len(self._pets)

    def add(self, pet: Pet) -> None:
        self._pets[pet.id] = pet

    def get(self, pet_id: UUID) -> Pet | None:
        return self._pets.get(pet_id)

    def list_by_owner(self, owner_id: UUID) -> list[Pet]:
        # Sorted by name, like the SQL repository.
        return sorted(
            (p for p in self._pets.values() if p.owner_id == owner_id),
            key=lambda p: p.name,
        )
