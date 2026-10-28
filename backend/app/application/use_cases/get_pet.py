from uuid import UUID

from app.application.ports import PetRepository
from app.domain.errors import PetNotFound
from app.domain.pet import Pet


class GetPet:
    def __init__(self, pets: PetRepository) -> None:
        self.pets = pets

    def execute(self, user_id: UUID, pet_id: UUID) -> Pet:
        pet = self.pets.get(pet_id)
        if pet is None:
            raise PetNotFound(f"Pet {pet_id} not found.")
        pet.ensure_owned_by(user_id)
        return pet
