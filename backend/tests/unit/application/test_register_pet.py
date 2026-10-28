from datetime import date, timedelta
from uuid import uuid4

import pytest

from app.application.use_cases.register_pet import RegisterPet
from app.domain.errors import InvalidPetData
from app.domain.pet import Species
from tests.unit.application.fakes import FakePetRepository


def test_registers_pet_for_owner():
    pets = FakePetRepository()
    owner_id = uuid4()

    pet = RegisterPet(pets).execute(owner_id=owner_id, name="Rex", species=Species.DOG)

    assert pet.owner_id == owner_id
    assert pets.get(pet.id) is pet


def test_does_not_save_invalid_pet():
    pets = FakePetRepository()

    with pytest.raises(InvalidPetData):
        RegisterPet(pets).execute(
            owner_id=uuid4(),
            name="Rex",
            species=Species.DOG,
            birth_date=date.today() + timedelta(days=1),
        )

    assert pets.pets == {}
