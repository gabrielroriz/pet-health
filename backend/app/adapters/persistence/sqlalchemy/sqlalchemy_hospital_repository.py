from uuid import UUID

from sqlalchemy import Row, Select, insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.adapters.persistence.sqlalchemy.sqlalchemy_tables import hospital_networks, hospitals
from app.domain.hospital import Hospital
from app.domain.hospital_network import HospitalNetwork


class SqlAlchemyHospitalRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # Not part of the port: hospitals are created by the seed and by tests.
    def add(self, hospital: Hospital) -> None:
        # Insert the network unless it exists, since hospitals of one network share it.
        if hospital.network is not None:
            self.session.execute(
                pg_insert(hospital_networks)
                .values(id=hospital.network.id, name=hospital.network.name)
                .on_conflict_do_nothing(index_elements=["id"])
            )
        # Then the hospital itself, linked to its network.
        self.session.execute(
            insert(hospitals).values(
                id=hospital.id,
                name=hospital.name,
                network_id=hospital.network.id if hospital.network else None,
            )
        )
        # Commit the network and the hospital together.
        self.session.commit()

    def get(self, hospital_id: UUID) -> Hospital | None:
        row = self.session.execute(_select_hospitals().where(hospitals.c.id == hospital_id)).one_or_none()
        return _to_hospital(row) if row else None

    def list_all(self) -> list[Hospital]:
        rows = self.session.execute(_select_hospitals().order_by(hospitals.c.name))
        return [_to_hospital(row) for row in rows]


# Hospitals with their network's name, if they have one.
def _select_hospitals() -> Select:
    return select(
        hospitals.c.id,
        hospitals.c.name,
        hospitals.c.network_id,
        hospital_networks.c.name.label("network_name"),
    ).outerjoin(hospital_networks, hospitals.c.network_id == hospital_networks.c.id)


def _to_hospital(row: Row) -> Hospital:
    # Rebuild the network only when the hospital has one.
    network = (
        HospitalNetwork(id=row.network_id, name=row.network_name)
        if row.network_id is not None
        else None
    )
    return Hospital(id=row.id, name=row.name, network=network)
