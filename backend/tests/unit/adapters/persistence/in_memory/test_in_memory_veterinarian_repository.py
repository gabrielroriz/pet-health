from uuid import uuid4

from app.adapters.persistence.in_memory.in_memory_veterinarian_repository import (
    InMemoryVeterinarianRepository,
)
from app.domain.veterinarian import Veterinarian


def test_lists_veterinarians_of_hospital():
    veterinarians = InMemoryVeterinarianRepository()
    downtown, riverside = uuid4(), uuid4()
    both = Veterinarian(name="Dr. Beatriz Costa", hospital_ids=frozenset({downtown, riverside}))
    riverside_only = Veterinarian(name="Dr. Daniela Rocha", hospital_ids=frozenset({riverside}))
    veterinarians.add(both)
    veterinarians.add(riverside_only)

    assert veterinarians.get(both.id) is both
    assert veterinarians.list_by_hospital(downtown) == [both]
    assert veterinarians.list_by_hospital(riverside) == [both, riverside_only]
