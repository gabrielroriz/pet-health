from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.appointment import Appointment


class AppointmentRepository(Protocol):
    # Each veterinarian's agenda has a version that every booking bumps. add() saves
    # only if the agenda is still at the version read before checking for overlaps,
    # and raises AgendaChanged otherwise. It raises DoubleBooking if the database
    # finds an overlap anyway.
    def agenda_version(self, veterinarian_id: UUID) -> int: ...

    def add(self, appointment: Appointment, agenda_version: int) -> None: ...

    # Saves changes to an existing appointment, such as a cancellation.
    def update(self, appointment: Appointment) -> None: ...

    def get(self, appointment_id: UUID) -> Appointment | None: ...

    # The user's appointments that still hold their slot, earliest first.
    def list_scheduled_by_owner(self, owner_id: UUID) -> list[Appointment]: ...

    # Scheduled appointments of any veterinarian or pet that overlap the period.
    def list_scheduled_overlapping(self, starts_at: datetime, ends_at: datetime) -> list[Appointment]: ...
