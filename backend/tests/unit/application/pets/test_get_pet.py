from uuid import uuid4

import pytest

from app.adapters.persistence.in_memory.in_memory_pet_repository import InMemoryPetRepository
from app.application.use_cases.pets.get_pet import GetPet
from app.domain.errors import NotAllowed, PetNotFound
from app.domain.pet import Pet, Species


@pytest.fixture
def pets() -> InMemoryPetRepository:
    return InMemoryPetRepository()


@pytest.fixture
def pet(pets: InMemoryPetRepository) -> Pet:
    pet = Pet(owner_id=uuid4(), name="Rex", species=Species.DOG)
    pets.add(pet)
    return pet


def test_owner_gets_pet(pets, pet):
    assert GetPet(pets).execute(user_id=pet.owner_id, pet_id=pet.id) is pet


def test_raises_when_pet_does_not_exist(pets):
    with pytest.raises(PetNotFound):
        GetPet(pets).execute(user_id=uuid4(), pet_id=uuid4())


def test_raises_when_pet_belongs_to_another_user(pets, pet):
    with pytest.raises(NotAllowed):
        GetPet(pets).execute(user_id=uuid4(), pet_id=pet.id)
