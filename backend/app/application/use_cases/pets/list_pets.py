from uuid import UUID

from app.application.ports.repositories.pet_repository import PetRepository
from app.domain.pet import Pet


class ListPets:
    def __init__(self, pets: PetRepository) -> None:
        self.pets = pets

    def execute(self, owner_id: UUID) -> list[Pet]:
        # Only the logged-in user's pets, sorted by name.
        return self.pets.list_by_owner(owner_id)
