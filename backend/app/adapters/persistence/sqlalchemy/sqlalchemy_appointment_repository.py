from datetime import datetime, timedelta
from uuid import UUID

from psycopg.errors import ExclusionViolation
from sqlalchemy import Executable, Row, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.adapters.persistence.sqlalchemy.sqlalchemy_tables import appointments, veterinarians
from app.domain.appointment import (
    AGENDA_CHANGED,
    PET_BUSY,
    VETERINARIAN_BUSY,
    Appointment,
    AppointmentStatus,
)
from app.domain.errors import AgendaChanged, DoubleBooking

# Maps each exclusion constraint to the message the client sees.
OVERLAP_MESSAGES = {
    "ex_appointments_veterinarian_overlap": VETERINARIAN_BUSY,
    "ex_appointments_pet_overlap": PET_BUSY,
}


class SqlAlchemyAppointmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # Current version of the veterinarian's agenda, read before checking for overlaps.
    def agenda_version(self, veterinarian_id: UUID) -> int:
        return self.session.execute(
            select(veterinarians.c.agenda_version).where(veterinarians.c.id == veterinarian_id)
        ).scalar_one()

    def add(self, appointment: Appointment, agenda_version: int) -> None:
        # Double-booking layer 2 (optimistic lock), part 2: bump the version only if it's unchanged.
        # The update locks the veterinarian's row until commit. A concurrent booking
        # for the same veterinarian waits here, then finds a newer version and fails.
        bumped = self.session.execute(
            update(veterinarians)
            .where(
                veterinarians.c.id == appointment.veterinarian_id,
                veterinarians.c.agenda_version == agenda_version,
            )
            .values(agenda_version=agenda_version + 1)
        )
        # No row matched: another booking changed the agenda since it was read.
        if bumped.rowcount == 0:
            self.session.rollback()
            raise AgendaChanged(AGENDA_CHANGED)
        # Insert in the same transaction as the version bump, then commit.
        self._write(insert(appointments).values(**_to_row(appointment)))

    # Write every field back, e.g. the cancelled status.
    def update(self, appointment: Appointment) -> None:
        self._write(
            update(appointments)
            .where(appointments.c.id == appointment.id)
            .values(**_to_row(appointment))
        )

    def get(self, appointment_id: UUID) -> Appointment | None:
        row = self.session.execute(
            select(appointments).where(appointments.c.id == appointment_id)
        ).one_or_none()
        return _to_appointment(row) if row else None

    # The owner's scheduled appointments, earliest first.
    def list_scheduled_by_owner(self, owner_id: UUID) -> list[Appointment]:
        rows = self.session.execute(
            select(appointments)
            .where(
                appointments.c.owner_id == owner_id,
                appointments.c.status == AppointmentStatus.SCHEDULED.value,
            )
            .order_by(appointments.c.starts_at)
        )
        return [_to_appointment(row) for row in rows]

    # Scheduled appointments that start before the period ends and end after it starts.
    def list_scheduled_overlapping(self, starts_at: datetime, ends_at: datetime) -> list[Appointment]:
        rows = self.session.execute(
            select(appointments).where(
                appointments.c.status == AppointmentStatus.SCHEDULED.value,
                appointments.c.starts_at < ends_at,
                appointments.c.ends_at > starts_at,
            )
        )
        return [_to_appointment(row) for row in rows]

    def _write(self, statement: Executable) -> None:
        # Double-booking layer 3 (database constraints): see ex_appointments_* in the migration.
        # The exclusion constraints are the last line of defense: they catch overlaps
        # even if a write skipped the checks in ScheduleAppointment.
        try:
            # PostgreSQL checks the exclusion constraints right here, as the statement runs.
            self.session.execute(statement)
            # Committing makes the change visible and releases its locks, so waiting bookings go on.
            self.session.commit()
        except IntegrityError as error:
            # Undo the failed transaction so the session can be reused.
            self.session.rollback()
            # Which constraint failed? Only our overlap constraints become DoubleBooking.
            constraint = (
                error.orig.diag.constraint_name
                if isinstance(error.orig, ExclusionViolation)
                else None
            )
            # Any other violation, like a foreign key, is a bug: let it surface as a 500.
            if constraint not in OVERLAP_MESSAGES:
                raise
            raise DoubleBooking(OVERLAP_MESSAGES[constraint]) from error


# Domain to row: the database stores ends_at instead of the duration.
def _to_row(appointment: Appointment) -> dict:
    return {
        "id": appointment.id,
        "owner_id": appointment.owner_id,
        "pet_id": appointment.pet_id,
        "hospital_id": appointment.hospital_id,
        "veterinarian_id": appointment.veterinarian_id,
        "starts_at": appointment.starts_at,
        "ends_at": appointment.ends_at,
        "reason": appointment.reason,
        "status": appointment.status.value,
    }


# Row to domain: the duration comes back from ends_at - starts_at.
def _to_appointment(row: Row) -> Appointment:
    return Appointment(
        id=row.id,
        owner_id=row.owner_id,
        pet_id=row.pet_id,
        hospital_id=row.hospital_id,
        veterinarian_id=row.veterinarian_id,
        starts_at=row.starts_at,
        duration_minutes=(row.ends_at - row.starts_at) // timedelta(minutes=1),
        reason=row.reason,
        status=AppointmentStatus(row.status),
    )
