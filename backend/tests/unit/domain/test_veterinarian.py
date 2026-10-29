from uuid import uuid4

import pytest

from app.domain.errors import InvalidAppointmentData
from app.domain.veterinarian import Veterinarian


def test_works_at_own_hospitals():
    hospital_id = uuid4()

    Veterinarian(name="Dr. Beatriz Costa", hospital_ids=frozenset({hospital_id})).ensure_works_at(
        hospital_id
    )


def test_does_not_work_at_other_hospitals():
    veterinarian = Veterinarian(name="Dr. Beatriz Costa", hospital_ids=frozenset({uuid4()}))

    with pytest.raises(InvalidAppointmentData):
        veterinarian.ensure_works_at(uuid4())
