from uuid import UUID

from sqlalchemy import Row, Select, func, insert, select
from sqlalchemy.orm import Session

from app.adapters.persistence.sqlalchemy.sqlalchemy_tables import (
    hospital_veterinarians,
    veterinarians,
)
from app.domain.veterinarian import Veterinarian


class SqlAlchemyVeterinarianRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # Not part of the port: veterinarians are created by the seed and by tests.
    def add(self, veterinarian: Veterinarian) -> None:
        # Insert the veterinarian, then one row per hospital they work at, in one transaction.
        self.session.execute(
            insert(veterinarians).values(id=veterinarian.id, name=veterinarian.name)
        )
        if veterinarian.hospital_ids:
            self.session.execute(
                insert(hospital_veterinarians),
                [
                    {"hospital_id": hospital_id, "veterinarian_id": veterinarian.id}
                    for hospital_id in veterinarian.hospital_ids
                ],
            )
        self.session.commit()

    def get(self, veterinarian_id: UUID) -> Veterinarian | None:
        row = self.session.execute(
            _select_veterinarians().where(veterinarians.c.id == veterinarian_id)
        ).one_or_none()
        return _to_veterinarian(row) if row else None

    def list_all(self) -> list[Veterinarian]:
        return [_to_veterinarian(row) for row in self.session.execute(_select_veterinarians())]

    def list_by_hospital(self, hospital_id: UUID) -> list[Veterinarian]:
        # Ids of the veterinarians who work at this hospital.
        works_there = select(hospital_veterinarians.c.veterinarian_id).where(
            hospital_veterinarians.c.hospital_id == hospital_id
        )
        rows = self.session.execute(_select_veterinarians().where(veterinarians.c.id.in_(works_there)))
        return [_to_veterinarian(row) for row in rows]


def _select_veterinarians() -> Select:
    # Collect each veterinarian's hospital ids into one array; FILTER skips the NULL of no hospital.
    hospital_ids = func.array_agg(hospital_veterinarians.c.hospital_id).filter(
        hospital_veterinarians.c.hospital_id.is_not(None)
    )
    return (
        select(veterinarians.c.id, veterinarians.c.name, hospital_ids.label("hospital_ids"))
        .outerjoin(hospital_veterinarians, hospital_veterinarians.c.veterinarian_id == veterinarians.c.id)
        .group_by(veterinarians.c.id)
        .order_by(veterinarians.c.name)
    )


# Convert a row into a domain Veterinarian; no hospitals comes back as NULL.
def _to_veterinarian(row: Row) -> Veterinarian:
    return Veterinarian(id=row.id, name=row.name, hospital_ids=frozenset(row.hospital_ids or ()))
