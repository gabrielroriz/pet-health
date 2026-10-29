from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.adapters.persistence.in_memory.in_memory_appointment_repository import (
    InMemoryAppointmentRepository,
)
from app.adapters.persistence.in_memory.in_memory_hospital_repository import (
    InMemoryHospitalRepository,
)
from app.adapters.persistence.in_memory.in_memory_veterinarian_repository import (
    InMemoryVeterinarianRepository,
)
from app.application.use_cases.veterinarians.list_available_veterinarians import (
    ListAvailableVeterinarians,
)
from app.domain.appointment import Appointment
from app.domain.errors import HospitalNotFound
from app.domain.hospital import Hospital
from app.domain.veterinarian import Veterinarian


def at(time: str) -> datetime:
    return datetime.fromisoformat(f"2030-01-01T{time}:00+00:00")


@pytest.fixture
def appointments() -> InMemoryAppointmentRepository:
    return InMemoryAppointmentRepository()


@pytest.fixture
def hospitals() -> InMemoryHospitalRepository:
    return InMemoryHospitalRepository()


@pytest.fixture
def veterinarians() -> InMemoryVeterinarianRepository:
    return InMemoryVeterinarianRepository()


@pytest.fixture
def downtown(hospitals) -> Hospital:
    hospital = Hospital(name="PetCare Downtown")
    hospitals.add(hospital)
    return hospital


@pytest.fixture
def riverside(hospitals) -> Hospital:
    hospital = Hospital(name="PetCare Riverside")
    hospitals.add(hospital)
    return hospital


def hire(veterinarians, name: str, *hospitals: Hospital) -> Veterinarian:
    veterinarian = Veterinarian(name=name, hospital_ids=frozenset(h.id for h in hospitals))
    veterinarians.add(veterinarian)
    return veterinarian


def book(appointments, veterinarian: Veterinarian, hospital: Hospital, time: str) -> Appointment:
    appointment = Appointment(
        owner_id=uuid4(),
        pet_id=uuid4(),
        hospital_id=hospital.id,
        veterinarian_id=veterinarian.id,
        starts_at=at(time),
        duration_minutes=30,
        reason="Check-up",
    )
    appointments.add(appointment, appointments.agenda_version(veterinarian.id))
    return appointment


def available(appointments, hospitals, veterinarians, hospital: Hospital, time: str) -> list[str]:
    use_case = ListAvailableVeterinarians(appointments, hospitals, veterinarians)
    return [v.name for v in use_case.execute(hospital.id, at(time), duration_minutes=30)]


def test_lists_veterinarians_of_hospital_without_overlapping_appointments(
    appointments, hospitals, veterinarians, downtown, riverside
):
    busy = hire(veterinarians, "Dr. Beatriz Costa", downtown)
    hire(veterinarians, "Dr. Carlos Lima", downtown)
    finishing_before = hire(veterinarians, "Dr. Daniela Rocha", downtown)
    hire(veterinarians, "Dr. Eduardo Alves", riverside)
    book(appointments, busy, downtown, "10:15")
    book(appointments, finishing_before, downtown, "09:30")

    assert available(appointments, hospitals, veterinarians, downtown, "10:00") == [
        "Dr. Carlos Lima",
        "Dr. Daniela Rocha",
    ]


def test_veterinarian_busy_at_another_hospital_is_unavailable(
    appointments, hospitals, veterinarians, downtown, riverside
):
    veterinarian = hire(veterinarians, "Dr. Beatriz Costa", downtown, riverside)
    book(appointments, veterinarian, riverside, "10:00")

    assert available(appointments, hospitals, veterinarians, downtown, "10:00") == []


def test_cancelled_appointment_frees_veterinarian(
    appointments, hospitals, veterinarians, downtown
):
    veterinarian = hire(veterinarians, "Dr. Beatriz Costa", downtown)
    appointment = book(appointments, veterinarian, downtown, "10:00")
    appointment.cancel()
    appointments.update(appointment)

    assert available(appointments, hospitals, veterinarians, downtown, "10:00") == [
        "Dr. Beatriz Costa"
    ]


def test_raises_when_hospital_does_not_exist(appointments, hospitals, veterinarians):
    with pytest.raises(HospitalNotFound):
        ListAvailableVeterinarians(appointments, hospitals, veterinarians).execute(
            uuid4(), at("10:00"), duration_minutes=30
        )
