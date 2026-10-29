from uuid import UUID

from app.application.ports.repositories.appointment_repository import AppointmentRepository
from app.domain.appointment import Appointment
from app.domain.errors import AppointmentNotFound


class CancelAppointment:
    def __init__(self, appointments: AppointmentRepository) -> None:
        self.appointments = appointments

    def execute(self, user_id: UUID, appointment_id: UUID) -> Appointment:
        # Load the appointment (404 if it doesn't exist).
        appointment = self.appointments.get(appointment_id)
        if appointment is None:
            raise AppointmentNotFound(f"Appointment {appointment_id} not found.")
        # Only the user who booked it may cancel it (403).
        appointment.ensure_owned_by(user_id)
        # Mark it cancelled (409 if it already was).
        appointment.cancel()
        # Persist the new status; its time is now free for other bookings.
        self.appointments.update(appointment)
        return appointment
