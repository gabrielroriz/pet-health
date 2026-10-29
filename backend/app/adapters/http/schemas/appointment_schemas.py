from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.appointment import Appointment, AppointmentStatus

# Allowed appointment lengths, shared with the availability query.
MIN_DURATION_MINUTES = 15
MAX_DURATION_MINUTES = 240


# Body of POST /appointments; unknown fields are rejected (422).
class ScheduleAppointmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pet_id: UUID
    hospital_id: UUID
    veterinarian_id: UUID
    # Must include a timezone, e.g. 2030-01-01T10:00:00Z.
    starts_at: AwareDatetime
    duration_minutes: int = Field(ge=MIN_DURATION_MINUTES, le=MAX_DURATION_MINUTES)
    reason: str = Field(min_length=1, max_length=500)


# JSON returned for an appointment, with ends_at computed from the duration.
class AppointmentResponse(BaseModel):
    id: UUID
    owner_id: UUID
    pet_id: UUID
    hospital_id: UUID
    veterinarian_id: UUID
    starts_at: datetime
    ends_at: datetime
    duration_minutes: int
    reason: str
    status: AppointmentStatus

    @classmethod
    def from_domain(cls, appointment: Appointment) -> Self:
        return cls(
            id=appointment.id,
            owner_id=appointment.owner_id,
            pet_id=appointment.pet_id,
            hospital_id=appointment.hospital_id,
            veterinarian_id=appointment.veterinarian_id,
            starts_at=appointment.starts_at,
            ends_at=appointment.ends_at,
            duration_minutes=appointment.duration_minutes,
            reason=appointment.reason,
            status=appointment.status,
        )
