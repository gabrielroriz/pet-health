from datetime import date
from uuid import uuid4

from app.adapters.persistence.sqlalchemy.sqlalchemy_pet_repository import SqlAlchemyPetRepository
from app.adapters.persistence.sqlalchemy.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.domain.pet import Pet, Species
from app.domain.user import User


def test_reads_added_pets_by_id_and_owner(session):
    owner = User(email="ana@example.com")
    SqlAlchemyUserRepository(session).add(owner)
    pets = SqlAlchemyPetRepository(session)
    thor = Pet(owner_id=owner.id, name="Thor", species=Species.DOG, birth_date=date(2020, 5, 1))
    luna = Pet(owner_id=owner.id, name="Luna", species=Species.CAT, breed="Siamese")

    pets.add(thor)
    pets.add(luna)

    assert pets.get(thor.id) == thor
    assert pets.list_by_owner(owner.id) == [luna, thor]
    assert pets.list_by_owner(uuid4()) == []


def test_returns_none_for_unknown_pet(session):
    assert SqlAlchemyPetRepository(session).get(uuid4()) is None
