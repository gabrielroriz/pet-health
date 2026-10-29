from datetime import datetime, timedelta
from uuid import UUID

from app.application.ports.repositories.appointment_repository import AppointmentRepository
from app.application.ports.repositories.hospital_repository import HospitalRepository
from app.application.ports.repositories.veterinarian_repository import VeterinarianRepository
from app.domain.errors import HospitalNotFound
from app.domain.veterinarian import Veterinarian


class ListAvailableVeterinarians:
    """Veterinarians of a hospital with no scheduled appointment in the given period, at any hospital."""

    def __init__(
        self,
        appointments: AppointmentRepository,
        hospitals: HospitalRepository,
        veterinarians: VeterinarianRepository,
    ) -> None:
        self.appointments = appointments
        self.hospitals = hospitals
        self.veterinarians = veterinarians

    def execute(
        self, hospital_id: UUID, starts_at: datetime, duration_minutes: int
    ) -> list[Veterinarian]:
        # The hospital must exist (404).
        if self.hospitals.get(hospital_id) is None:
            raise HospitalNotFound(f"Hospital {hospital_id} not found.")
        # The period the appointment would occupy.
        ends_at = starts_at + timedelta(minutes=duration_minutes)
        # Veterinarians already booked during that period, at any hospital.
        busy = {
            appointment.veterinarian_id
            for appointment in self.appointments.list_scheduled_overlapping(starts_at, ends_at)
        }
        # The hospital's veterinarians minus the busy ones.
        return [
            veterinarian
            for veterinarian in self.veterinarians.list_by_hospital(hospital_id)
            if veterinarian.id not in busy
        ]
