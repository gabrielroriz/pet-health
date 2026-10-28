from datetime import date, timedelta
from uuid import uuid4

import pytest

from app.domain.errors import InvalidPetData, NotAllowed
from app.domain.pet import Pet, Species


def make_pet(**overrides) -> Pet:
    data = {"owner_id": uuid4(), "name": "Rex", "species": Species.DOG}
    return Pet(**(data | overrides))


def test_creates_pet_with_generated_id():
    pet = make_pet()

    assert pet.id is not None
    assert pet.name == "Rex"
    assert pet.species is Species.DOG


def test_strips_name():
    assert make_pet(name="  Rex  ").name == "Rex"


@pytest.mark.parametrize("name", ["", "   "])
def test_rejects_blank_name(name):
    with pytest.raises(InvalidPetData):
        make_pet(name=name)


def test_accepts_birth_date_today():
    assert make_pet(birth_date=date.today()).birth_date == date.today()


def test_rejects_birth_date_in_the_future():
    with pytest.raises(InvalidPetData):
        make_pet(birth_date=date.today() + timedelta(days=1))


def test_blank_breed_becomes_none():
    assert make_pet(breed="  ").breed is None


def test_owner_passes_ownership_check():
    pet = make_pet()

    pet.ensure_owned_by(pet.owner_id)


def test_other_user_fails_ownership_check():
    with pytest.raises(NotAllowed):
        make_pet().ensure_owned_by(uuid4())
