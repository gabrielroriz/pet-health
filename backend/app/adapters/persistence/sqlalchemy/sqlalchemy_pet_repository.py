from uuid import UUID

from sqlalchemy import Row, insert, select
from sqlalchemy.orm import Session

from app.adapters.persistence.sqlalchemy.sqlalchemy_tables import pets
from app.domain.pet import Pet, Species


class SqlAlchemyPetRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, pet: Pet) -> None:
        # Insert and commit at once: each repository write is its own transaction.
        self.session.execute(
            insert(pets).values(
                id=pet.id,
                owner_id=pet.owner_id,
                name=pet.name,
                species=pet.species.value,
                birth_date=pet.birth_date,
                breed=pet.breed,
            )
        )
        self.session.commit()

    def get(self, pet_id: UUID) -> Pet | None:
        row = self.session.execute(select(pets).where(pets.c.id == pet_id)).one_or_none()
        return _to_pet(row) if row else None

    def list_by_owner(self, owner_id: UUID) -> list[Pet]:
        # The owner's pets, sorted by name.
        rows = self.session.execute(
            select(pets).where(pets.c.owner_id == owner_id).order_by(pets.c.name)
        )
        return [_to_pet(row) for row in rows]


# Convert a database row back into a domain Pet.
def _to_pet(row: Row) -> Pet:
    return Pet(
        id=row.id,
        owner_id=row.owner_id,
        name=row.name,
        species=Species(row.species),
        birth_date=row.birth_date,
        breed=row.breed,
    )
