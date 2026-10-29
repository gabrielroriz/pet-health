"""Development data: a hospital network, hospitals, veterinarians, and users with their pets.

Run it with `python -m app.seed` after migrating. Running it again changes nothing.
"""

from datetime import date
from typing import NamedTuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.adapters.persistence.sqlalchemy.sqlalchemy_hospital_repository import (
    SqlAlchemyHospitalRepository,
)
from app.adapters.persistence.sqlalchemy.sqlalchemy_pet_repository import SqlAlchemyPetRepository
from app.adapters.persistence.sqlalchemy.sqlalchemy_session import create_session_factory
from app.adapters.persistence.sqlalchemy.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.adapters.persistence.sqlalchemy.sqlalchemy_veterinarian_repository import (
    SqlAlchemyVeterinarianRepository,
)
from app.config import settings
from app.domain.hospital import Hospital
from app.domain.hospital_network import HospitalNetwork
from app.domain.pet import Pet, Species
from app.domain.user import User
from app.domain.veterinarian import Veterinarian

# Fixed ids make the seed idempotent: a second run finds these rows and skips them.
PETCARE = HospitalNetwork(id=UUID("6eb3ed06-e33f-4016-8130-3930e39a9105"), name="PetCare Network")
DOWNTOWN = Hospital(
    id=UUID("1cad8cf3-9c99-4c63-9762-dc92f6a8668a"), name="PetCare Downtown", network=PETCARE
)
RIVERSIDE = Hospital(
    id=UUID("a5990571-8262-4499-9ab9-d1c3e3ee3102"), name="PetCare Riverside", network=PETCARE
)
HAPPY_PAWS = Hospital(id=UUID("4cc6545d-13d0-485d-a420-57d4da978945"), name="Happy Paws Clinic")

VETERINARIANS = [
    # Works at two hospitals of the network.
    Veterinarian(
        id=UUID("3e36e9ad-e40c-463c-9072-6d7d5972b835"),
        name="Dr. Beatriz Costa",
        hospital_ids=frozenset({DOWNTOWN.id, RIVERSIDE.id}),
    ),
    Veterinarian(
        id=UUID("9ddd115b-cdc0-413c-99eb-5080afc77455"),
        name="Dr. Carlos Lima",
        hospital_ids=frozenset({DOWNTOWN.id}),
    ),
    Veterinarian(
        id=UUID("360a2fcf-05be-438a-92df-fa5252752712"),
        name="Dr. Daniela Rocha",
        hospital_ids=frozenset({RIVERSIDE.id}),
    ),
    Veterinarian(
        id=UUID("5d9a3409-a8f5-454b-b84c-9600ee6fce61"),
        name="Dr. Eduardo Alves",
        hospital_ids=frozenset({HAPPY_PAWS.id}),
    ),
]


# A pet to create; its owner is the user it's listed under.
class SeedPet(NamedTuple):
    name: str
    species: Species
    breed: str | None = None
    birth_date: date | None = None


# Log in with one of these emails to book appointments for its pets.
PETS_BY_OWNER = {
    "ana@example.com": [
        SeedPet("Thor", Species.DOG, "Golden Retriever", date(2019, 4, 12)),
        SeedPet("Luna", Species.CAT, "Siamese", date(2021, 8, 3)),
        SeedPet("Mel", Species.RABBIT, "Mini Lop", date(2023, 2, 20)),
        SeedPet("Kiwi", Species.BIRD, "Cockatiel", date(2022, 11, 5)),
    ],
    "bob@example.com": [
        SeedPet("Rex", Species.DOG, "Beagle", date(2020, 5, 1)),
        # Mixed breed, so no breed.
        SeedPet("Mia", Species.CAT, birth_date=date(2018, 9, 15)),
        # Adopted as an adult, birth date unknown.
        SeedPet("Shelly", Species.OTHER, "Red-eared slider turtle"),
    ],
}


def seed(session: Session) -> None:
    # Hospitals first, with their network, since veterinarians reference them.
    hospitals = SqlAlchemyHospitalRepository(session)
    for hospital in (DOWNTOWN, RIVERSIDE, HAPPY_PAWS):
        if hospitals.get(hospital.id) is None:
            hospitals.add(hospital)

    # Then the veterinarians and the hospitals they work at.
    veterinarians = SqlAlchemyVeterinarianRepository(session)
    for veterinarian in VETERINARIANS:
        if veterinarians.get(veterinarian.id) is None:
            veterinarians.add(veterinarian)

    users = SqlAlchemyUserRepository(session)
    pets = SqlAlchemyPetRepository(session)
    for email, owner_pets in PETS_BY_OWNER.items():
        # The owner, reused if they already logged in.
        user = users.get_by_email(email)
        if user is None:
            user = User(email=email)
            users.add(user)

        # Their pets, skipping any they already have with the same name.
        existing = {pet.name for pet in pets.list_by_owner(user.id)}
        for pet in owner_pets:
            if pet.name not in existing:
                pets.add(Pet(owner_id=user.id, **pet._asdict()))


if __name__ == "__main__":
    # Connect to DATABASE_URL and insert whatever is missing.
    with create_session_factory(settings.database_url)() as session:
        seed(session)
    print("Development data is in place.")
