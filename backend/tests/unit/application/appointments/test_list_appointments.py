from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.adapters.persistence.in_memory.in_memory_appointment_repository import (
    InMemoryAppointmentRepository,
)
from app.application.use_cases.appointments.list_appointments import ListAppointments
from app.domain.appointment import Appointment


def book(appointments: InMemoryAppointmentRepository, owner_id: UUID, hour: int) -> Appointment:
    appointment = Appointment(
        owner_id=owner_id,
        pet_id=uuid4(),
        hospital_id=uuid4(),
        veterinarian_id=uuid4(),
        starts_at=datetime(2030, 1, 1, hour, tzinfo=UTC),
        duration_minutes=30,
        reason="Check-up",
    )
    appointments.add(appointment, agenda_version=0)
    return appointment


def test_lists_scheduled_appointments_of_owner_earliest_first():
    appointments = InMemoryAppointmentRepository()
    owner_id = uuid4()
    later = book(appointments, owner_id, hour=15)
    earlier = book(appointments, owner_id, hour=9)
    cancelled = book(appointments, owner_id, hour=11)
    cancelled.cancel()
    appointments.update(cancelled)
    book(appointments, uuid4(), hour=10)

    assert ListAppointments(appointments).execute(owner_id) == [earlier, later]
