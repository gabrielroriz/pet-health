from datetime import date
from uuid import UUID

from app.application.ports.repositories.pet_repository import PetRepository
from app.domain.pet import Pet, Species


class RegisterPet:
    def __init__(self, pets: PetRepository) -> None:
        self.pets = pets

    def execute(
        self,
        owner_id: UUID,
        name: str,
        species: Species,
        birth_date: date | None = None,
        breed: str | None = None,
    ) -> Pet:
        # Building the Pet runs its business rules, so an invalid pet is never saved.
        pet = Pet(
            owner_id=owner_id,
            name=name,
            species=species,
            birth_date=birth_date,
            breed=breed,
        )
        # Store it, owned by the logged-in user.
        self.pets.add(pet)
        return pet
