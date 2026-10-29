from uuid import UUID

from app.application.ports.repositories.appointment_repository import AppointmentRepository
from app.domain.appointment import Appointment


class ListAppointments:
    def __init__(self, appointments: AppointmentRepository) -> None:
        self.appointments = appointments

    def execute(self, owner_id: UUID) -> list[Appointment]:
        # Cancelled appointments stay in the database as history but aren't listed.
        return self.appointments.list_scheduled_by_owner(owner_id)
