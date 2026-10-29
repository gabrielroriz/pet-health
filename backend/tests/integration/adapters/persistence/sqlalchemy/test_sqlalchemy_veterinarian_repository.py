from uuid import uuid4

from app.adapters.persistence.sqlalchemy.sqlalchemy_veterinarian_repository import (
    SqlAlchemyVeterinarianRepository,
)
from tests.integration.conftest import add_hospital, add_veterinarian


def test_reads_veterinarians_with_their_hospitals(session):
    downtown = add_hospital(session, "PetCare Downtown")
    riverside = add_hospital(session, "PetCare Riverside")
    daniela = add_veterinarian(session, riverside, name="Dr. Daniela Rocha")
    beatriz = add_veterinarian(session, downtown, riverside, name="Dr. Beatriz Costa")
    newcomer = add_veterinarian(session, name="Dr. Carlos Lima")
    veterinarians = SqlAlchemyVeterinarianRepository(session)

    assert veterinarians.get(beatriz.id) == beatriz
    assert veterinarians.list_all() == [beatriz, newcomer, daniela]
    assert veterinarians.list_by_hospital(downtown.id) == [beatriz]
    assert veterinarians.list_by_hospital(riverside.id) == [beatriz, daniela]


def test_returns_none_for_unknown_veterinarian(session):
    assert SqlAlchemyVeterinarianRepository(session).get(uuid4()) is None
