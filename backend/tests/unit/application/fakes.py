from uuid import UUID

from app.domain.pet import Pet


class FakePetRepository:
    def __init__(self) -> None:
        self.pets: dict[UUID, Pet] = {}

    def add(self, pet: Pet) -> None:
        self.pets[pet.id] = pet

    def get(self, pet_id: UUID) -> Pet | None:
        return self.pets.get(pet_id)
