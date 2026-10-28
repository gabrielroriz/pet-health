from uuid import uuid4

from app.adapters.persistence.in_memory.in_memory_pet_repository import InMemoryPetRepository
from app.domain.pet import Pet, Species


def test_gets_added_pet():
    pets = InMemoryPetRepository()
    pet = Pet(owner_id=uuid4(), name="Rex", species=Species.DOG)

    pets.add(pet)

    assert pets.get(pet.id) is pet
    assert len(pets) == 1


def test_returns_none_for_unknown_pet():
    assert InMemoryPetRepository().get(uuid4()) is None
