from uuid import uuid4

from app.adapters.persistence.sqlalchemy.sqlalchemy_hospital_repository import (
    SqlAlchemyHospitalRepository,
)
from app.domain.hospital_network import HospitalNetwork
from tests.integration.conftest import add_hospital


def test_reads_hospitals_with_their_network(session):
    network = HospitalNetwork(name="PetCare Network")
    riverside = add_hospital(session, "PetCare Riverside", network)
    downtown = add_hospital(session, "PetCare Downtown", network)
    happy_paws = add_hospital(session, "Happy Paws Clinic")
    hospitals = SqlAlchemyHospitalRepository(session)

    assert hospitals.get(riverside.id) == riverside
    assert hospitals.list_all() == [happy_paws, downtown, riverside]


def test_returns_none_for_unknown_hospital(session):
    assert SqlAlchemyHospitalRepository(session).get(uuid4()) is None
