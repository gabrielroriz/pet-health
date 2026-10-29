from datetime import datetime
from uuid import UUID

from app.domain.appointment import AGENDA_CHANGED, Appointment, AppointmentStatus
from app.domain.errors import AgendaChanged


class InMemoryAppointmentRepository:
    """Applies the same agenda version check and no-overlap rule as the database."""

    def __init__(self) -> None:
        self._appointments: dict[UUID, Appointment] = {}
        self._agenda_versions: dict[UUID, int] = {}

    def __len__(self) -> int:
        return len(self._appointments)

    def agenda_version(self, veterinarian_id: UUID) -> int:
        # Version 0 until the veterinarian's first booking.
        return self._agenda_versions.get(veterinarian_id, 0)

    def add(self, appointment: Appointment, agenda_version: int) -> None:
        # Layer 2 (optimistic lock): refuse if another booking bumped the version since it was read.
        if self.agenda_version(appointment.veterinarian_id) != agenda_version:
            raise AgendaChanged(AGENDA_CHANGED)
        # Layer 3 stand-in: what the database's exclusion constraints do.
        appointment.ensure_no_conflict_with(self._appointments.values())
        # Bump the version and keep the appointment.
        self._agenda_versions[appointment.veterinarian_id] = agenda_version + 1
        self._appointments[appointment.id] = appointment

    def update(self, appointment: Appointment) -> None:
        self._appointments[appointment.id] = appointment

    def get(self, appointment_id: UUID) -> Appointment | None:
        return self._appointments.get(appointment_id)

    def list_scheduled_by_owner(self, owner_id: UUID) -> list[Appointment]:
        return sorted(
            (a for a in self._scheduled() if a.owner_id == owner_id),
            key=lambda a: a.starts_at,
        )

    def list_scheduled_overlapping(self, starts_at: datetime, ends_at: datetime) -> list[Appointment]:
        # Same overlap test as the SQL query: starts before the period ends, ends after it starts.
        return [a for a in self._scheduled() if a.starts_at < ends_at and starts_at < a.ends_at]

    def _scheduled(self) -> list[Appointment]:
        return [a for a in self._appointments.values() if a.status is AppointmentStatus.SCHEDULED]
