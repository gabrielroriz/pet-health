from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.errors import (
    AppointmentAlreadyCancelled,
    DoubleBooking,
    InvalidAppointmentData,
    NotAllowed,
)

# Shared by the domain check and the database adapter, so both report the same message.
VETERINARIAN_BUSY = "The veterinarian already has an appointment at this time. Choose another time."
PET_BUSY = "This pet already has an appointment at this time. Choose another time."
AGENDA_CHANGED = "The veterinarian's agenda changed while booking. Try again."


class AppointmentStatus(StrEnum):
    # Holds its time slot.
    SCHEDULED = "scheduled"
    # Kept as history; its time slot is free again.
    CANCELLED = "cancelled"


@dataclass
class Appointment:
    # The user who booked it; only they can see and cancel it.
    owner_id: UUID
    pet_id: UUID
    hospital_id: UUID
    veterinarian_id: UUID
    starts_at: datetime
    duration_minutes: int
    reason: str
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        # Runs on every Appointment, new or loaded from the database: rules that always hold.
        if self.starts_at.tzinfo is None:
            raise InvalidAppointmentData("Start time must include a timezone.")
        if self.duration_minutes <= 0:
            raise InvalidAppointmentData("Duration must be positive.")
        self.reason = self.reason.strip()
        if not self.reason:
            raise InvalidAppointmentData("Reason must not be blank.")

    @property
    def ends_at(self) -> datetime:
        # Derived from the duration; the database stores it so its constraints can compare time ranges.
        return self.starts_at + timedelta(minutes=self.duration_minutes)

    # Back-to-back appointments are allowed: one may start exactly when another ends.
    def overlaps(self, other: "Appointment") -> bool:
        return self.starts_at < other.ends_at and other.starts_at < self.ends_at

    def ensure_no_conflict_with(self, others: Iterable["Appointment"]) -> None:
        # Double-booking layer 1: the business rule, checked before anything is saved.
        for other in others:
            # Ignore itself, cancelled appointments and those at other times.
            if (
                other.id == self.id
                or other.status is not AppointmentStatus.SCHEDULED
                or not self.overlaps(other)
            ):
                continue
            # The veterinarian can't be in two appointments at once.
            if other.veterinarian_id == self.veterinarian_id:
                raise DoubleBooking(VETERINARIAN_BUSY)
            # Neither can the pet, even with another veterinarian.
            if other.pet_id == self.pet_id:
                raise DoubleBooking(PET_BUSY)

    def ensure_starts_after(self, moment: datetime) -> None:
        # Checked only when booking, since stored appointments eventually fall in the past.
        if self.starts_at <= moment:
            raise InvalidAppointmentData("Appointments must start in the future.")

    def ensure_owned_by(self, user_id: UUID) -> None:
        # Only the user who booked it may cancel it.
        if self.owner_id != user_id:
            raise NotAllowed("This appointment belongs to another user.")

    def cancel(self) -> None:
        # Cancelling twice is reported as a conflict instead of silently ignored.
        if self.status is AppointmentStatus.CANCELLED:
            raise AppointmentAlreadyCancelled("This appointment is already cancelled.")
        self.status = AppointmentStatus.CANCELLED
