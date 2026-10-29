from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.adapters.persistence.in_memory.in_memory_appointment_repository import (
    InMemoryAppointmentRepository,
)
from app.domain.appointment import Appointment
from app.domain.errors import AgendaChanged, DoubleBooking


def make_appointment(hour: int, veterinarian_id: UUID | None = None) -> Appointment:
    return Appointment(
        owner_id=uuid4(),
        pet_id=uuid4(),
        hospital_id=uuid4(),
        veterinarian_id=veterinarian_id or uuid4(),
        starts_at=datetime(2030, 1, 1, hour, tzinfo=UTC),
        duration_minutes=60,
        reason="Check-up",
    )


def test_adding_bumps_agenda_version_of_veterinarian():
    appointments = InMemoryAppointmentRepository()
    appointment = make_appointment(10)

    appointments.add(appointment, agenda_version=0)

    assert appointments.get(appointment.id) is appointment
    assert appointments.agenda_version(appointment.veterinarian_id) == 1


def test_rejects_stale_agenda_version():
    appointments = InMemoryAppointmentRepository()
    first = make_appointment(10)
    appointments.add(first, agenda_version=0)

    with pytest.raises(AgendaChanged):
        appointments.add(make_appointment(14, first.veterinarian_id), agenda_version=0)

    assert len(appointments) == 1


def test_rejects_overlap_like_the_database_constraint():
    appointments = InMemoryAppointmentRepository()
    first = make_appointment(10)
    appointments.add(first, agenda_version=0)

    with pytest.raises(DoubleBooking):
        appointments.add(make_appointment(10, first.veterinarian_id), agenda_version=1)


def test_lists_scheduled_appointments_overlapping_period():
    appointments = InMemoryAppointmentRepository()
    nine, ten, eleven = make_appointment(9), make_appointment(10), make_appointment(11)
    for appointment in (nine, ten, eleven):
        appointments.add(appointment, agenda_version=0)
    eleven.cancel()
    appointments.update(eleven)

    listed = appointments.list_scheduled_overlapping(
        datetime(2030, 1, 1, 10, 30, tzinfo=UTC), datetime(2030, 1, 1, 11, 30, tzinfo=UTC)
    )

    assert listed == [ten]
