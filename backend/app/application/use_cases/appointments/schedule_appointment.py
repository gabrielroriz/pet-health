from datetime import UTC, datetime
from uuid import UUID

from app.application.ports.repositories.appointment_repository import AppointmentRepository
from app.application.ports.repositories.hospital_repository import HospitalRepository
from app.application.ports.repositories.pet_repository import PetRepository
from app.application.ports.repositories.veterinarian_repository import VeterinarianRepository
from app.domain.appointment import Appointment
from app.domain.errors import AgendaChanged, HospitalNotFound, PetNotFound, VeterinarianNotFound

# Concurrent bookings for the same veterinarian bump the same agenda version, so all
# but one fail with AgendaChanged. Each retry reads the agenda again: a booking that
# overlaps the winner then fails with DoubleBooking, any other one goes through.
MAX_ATTEMPTS = 3


# Books an appointment. Double booking is blocked in 3 layers, explained in docs/ARCHITECTURE.md.
class ScheduleAppointment:
    def __init__(
        self,
        appointments: AppointmentRepository,
        pets: PetRepository,
        hospitals: HospitalRepository,
        veterinarians: VeterinarianRepository,
    ) -> None:
        self.appointments = appointments
        self.pets = pets
        self.hospitals = hospitals
        self.veterinarians = veterinarians

    def execute(
        self,
        owner_id: UUID,
        pet_id: UUID,
        hospital_id: UUID,
        veterinarian_id: UUID,
        starts_at: datetime,
        duration_minutes: int,
        reason: str,
    ) -> Appointment:
        # 1. The pet must exist (404) and belong to the user booking (403).
        pet = self.pets.get(pet_id)
        if pet is None:
            raise PetNotFound(f"Pet {pet_id} not found.")
        pet.ensure_owned_by(owner_id)
        # 2. The hospital must exist (404).
        if self.hospitals.get(hospital_id) is None:
            raise HospitalNotFound(f"Hospital {hospital_id} not found.")
        # 3. The veterinarian must exist (404) and work at that hospital (422).
        veterinarian = self.veterinarians.get(veterinarian_id)
        if veterinarian is None:
            raise VeterinarianNotFound(f"Veterinarian {veterinarian_id} not found.")
        veterinarian.ensure_works_at(hospital_id)

        # 4. Building the appointment validates timezone, duration and reason (422).
        appointment = Appointment(
            owner_id=owner_id,
            pet_id=pet_id,
            hospital_id=hospital_id,
            veterinarian_id=veterinarian_id,
            starts_at=starts_at,
            duration_minutes=duration_minutes,
            reason=reason,
        )
        # 5. It must start in the future (422).
        appointment.ensure_starts_after(datetime.now(UTC))

        # 6. Book it, retrying when a concurrent booking changed the veterinarian's agenda first.
        for _ in range(MAX_ATTEMPTS - 1):
            try:
                return self._book(appointment)
            except AgendaChanged:
                # Someone booked this veterinarian in between: read the agenda again and recheck.
                continue
        # Last attempt: if the agenda changed yet again, AgendaChanged reaches the client as a 409.
        return self._book(appointment)

    def _book(self, appointment: Appointment) -> Appointment:
        # Double-booking layer 2 (optimistic lock), part 1: note the agenda version first.
        # Read the version before checking for overlaps, so a booking saved in
        # between makes add() fail instead of slipping past the check.
        agenda_version = self.appointments.agenda_version(appointment.veterinarian_id)
        # Double-booking layer 1 (domain check): 409 if the veterinarian or the pet is busy then.
        appointment.ensure_no_conflict_with(
            self.appointments.list_scheduled_overlapping(appointment.starts_at, appointment.ends_at)
        )
        # Layers 2 and 3: save only if the version is unchanged; the database rejects any overlap left.
        self.appointments.add(appointment, agenda_version)
        return appointment
