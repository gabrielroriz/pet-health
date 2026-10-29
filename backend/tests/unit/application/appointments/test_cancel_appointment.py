from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.adapters.persistence.in_memory.in_memory_appointment_repository import (
    InMemoryAppointmentRepository,
)
from app.application.use_cases.appointments.cancel_appointment import CancelAppointment
from app.domain.appointment import Appointment, AppointmentStatus
from app.domain.errors import AppointmentAlreadyCancelled, AppointmentNotFound, NotAllowed


@pytest.fixture
def appointments() -> InMemoryAppointmentRepository:
    return InMemoryAppointmentRepository()


@pytest.fixture
def appointment(appointments) -> Appointment:
    appointment = Appointment(
        owner_id=uuid4(),
        pet_id=uuid4(),
        hospital_id=uuid4(),
        veterinarian_id=uuid4(),
        starts_at=datetime(2030, 1, 1, 10, tzinfo=UTC),
        duration_minutes=30,
        reason="Check-up",
    )
    appointments.add(appointment, agenda_version=0)
    return appointment


def test_owner_cancels_appointment_and_frees_its_time(appointments, appointment):
    cancelled = CancelAppointment(appointments).execute(
        user_id=appointment.owner_id, appointment_id=appointment.id
    )

    assert cancelled.status is AppointmentStatus.CANCELLED
    assert appointments.list_scheduled_overlapping(appointment.starts_at, appointment.ends_at) == []


def test_raises_when_appointment_does_not_exist(appointments):
    with pytest.raises(AppointmentNotFound):
        CancelAppointment(appointments).execute(user_id=uuid4(), appointment_id=uuid4())


def test_raises_when_appointment_belongs_to_another_user(appointments, appointment):
    with pytest.raises(NotAllowed):
        CancelAppointment(appointments).execute(user_id=uuid4(), appointment_id=appointment.id)

    assert appointment.status is AppointmentStatus.SCHEDULED


def test_raises_when_appointment_is_already_cancelled(appointments, appointment):
    cancel = CancelAppointment(appointments)
    cancel.execute(user_id=appointment.owner_id, appointment_id=appointment.id)

    with pytest.raises(AppointmentAlreadyCancelled):
        cancel.execute(user_id=appointment.owner_id, appointment_id=appointment.id)
