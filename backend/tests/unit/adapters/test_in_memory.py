from uuid import uuid4

from app.adapters.persistence.in_memory import (
    InMemoryPetRepository,
    InMemoryUserRepository,
)
from app.domain.pet import Pet, Species
from app.domain.user import User


def test_gets_added_pet():
    pets = InMemoryPetRepository()
    pet = Pet(owner_id=uuid4(), name="Rex", species=Species.DOG)

    pets.add(pet)

    assert pets.get(pet.id) is pet
    assert len(pets) == 1


def test_returns_none_for_unknown_pet():
    assert InMemoryPetRepository().get(uuid4()) is None



def test_gets_added_user_by_id_and_email():
    users = InMemoryUserRepository()
    user = User(email="ana@example.com")

    users.add(user)

    assert users.get(user.id) is user
    assert users.get_by_email("ana@example.com") is user
    assert users.get_by_email("bob@example.com") is None
