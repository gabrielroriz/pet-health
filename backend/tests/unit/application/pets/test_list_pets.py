from uuid import uuid4

from app.adapters.persistence.in_memory.in_memory_pet_repository import InMemoryPetRepository
from app.application.use_cases.pets.list_pets import ListPets
from app.domain.pet import Pet, Species


def test_lists_pets_of_owner_by_name():
    pets = InMemoryPetRepository()
    owner_id = uuid4()
    thor = Pet(owner_id=owner_id, name="Thor", species=Species.DOG)
    luna = Pet(owner_id=owner_id, name="Luna", species=Species.CAT)
    for pet in (thor, luna, Pet(owner_id=uuid4(), name="Rex", species=Species.DOG)):
        pets.add(pet)

    assert ListPets(pets).execute(owner_id) == [luna, thor]
