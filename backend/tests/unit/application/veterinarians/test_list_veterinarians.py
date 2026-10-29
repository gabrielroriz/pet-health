from uuid import uuid4

from app.adapters.persistence.in_memory.in_memory_veterinarian_repository import (
    InMemoryVeterinarianRepository,
)
from app.application.use_cases.veterinarians.list_veterinarians import ListVeterinarians
from app.domain.veterinarian import Veterinarian


def test_lists_veterinarians_by_name():
    veterinarians = InMemoryVeterinarianRepository()
    carlos = Veterinarian(name="Dr. Carlos Lima", hospital_ids=frozenset({uuid4()}))
    beatriz = Veterinarian(name="Dr. Beatriz Costa", hospital_ids=frozenset({uuid4()}))
    veterinarians.add(carlos)
    veterinarians.add(beatriz)

    assert ListVeterinarians(veterinarians).execute() == [beatriz, carlos]
