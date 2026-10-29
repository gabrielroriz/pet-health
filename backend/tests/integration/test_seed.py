from app.adapters.persistence.sqlalchemy.sqlalchemy_hospital_repository import (
    SqlAlchemyHospitalRepository,
)
from app.adapters.persistence.sqlalchemy.sqlalchemy_pet_repository import SqlAlchemyPetRepository
from app.adapters.persistence.sqlalchemy.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.adapters.persistence.sqlalchemy.sqlalchemy_veterinarian_repository import (
    SqlAlchemyVeterinarianRepository,
)
from app.domain.pet import Pet, Species
from app.domain.user import User
from app.seed import PETS_BY_OWNER, VETERINARIANS, seed


def pets_of(session, email: str) -> list[Pet]:
    user = SqlAlchemyUserRepository(session).get_by_email(email)
    assert user is not None
    return SqlAlchemyPetRepository(session).list_by_owner(user.id)


def test_seeds_everything_once(session):
    seed(session)
    seed(session)

    assert len(SqlAlchemyHospitalRepository(session).list_all()) == 3
    assert len(SqlAlchemyVeterinarianRepository(session).list_all()) == len(VETERINARIANS)
    for email, owner_pets in PETS_BY_OWNER.items():
        assert sorted(p.name for p in pets_of(session, email)) == sorted(p.name for p in owner_pets)


def test_saves_every_pet_field(session):
    seed(session)

    thor = next(p for p in pets_of(session, "ana@example.com") if p.name == "Thor")
    expected = next(p for p in PETS_BY_OWNER["ana@example.com"] if p.name == "Thor")
    assert (thor.species, thor.breed, thor.birth_date) == (
        expected.species,
        expected.breed,
        expected.birth_date,
    )


def test_completes_the_pets_of_a_user_who_already_logged_in(session):
    ana = User(email="ana@example.com")
    SqlAlchemyUserRepository(session).add(ana)
    SqlAlchemyPetRepository(session).add(Pet(owner_id=ana.id, name="Thor", species=Species.DOG))

    seed(session)

    names = [p.name for p in pets_of(session, "ana@example.com")]
    assert sorted(names) == sorted(p.name for p in PETS_BY_OWNER["ana@example.com"])
    assert pets_of(session, "ana@example.com")[0].owner_id == ana.id
