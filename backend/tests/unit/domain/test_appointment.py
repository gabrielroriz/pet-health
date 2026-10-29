from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.appointment import PET_BUSY, VETERINARIAN_BUSY, Appointment, AppointmentStatus
from app.domain.errors import (
    AppointmentAlreadyCancelled,
    DoubleBooking,
    InvalidAppointmentData,
    NotAllowed,
)


def at(time: str, duration_minutes: int = 30, **overrides) -> Appointment:
    data = {
        "owner_id": uuid4(),
        "pet_id": uuid4(),
        "hospital_id": uuid4(),
        "veterinarian_id": uuid4(),
        "starts_at": datetime.fromisoformat(f"2030-01-01T{time}:00+00:00"),
        "duration_minutes": duration_minutes,
        "reason": "Check-up",
    }
    return Appointment(**(data | overrides))


def test_creates_scheduled_appointment_ending_after_its_duration():
    appointment = at("10:00", duration_minutes=45)

    assert appointment.status is AppointmentStatus.SCHEDULED
    assert appointment.ends_at == datetime(2030, 1, 1, 10, 45, tzinfo=UTC)


def test_strips_reason():
    assert at("10:00", reason="  Vaccines  ").reason == "Vaccines"


@pytest.mark.parametrize("reason", ["", "   "])
def test_rejects_blank_reason(reason):
    with pytest.raises(InvalidAppointmentData):
        at("10:00", reason=reason)


def test_rejects_start_without_timezone():
    with pytest.raises(InvalidAppointmentData):
        at("10:00", starts_at=datetime(2030, 1, 1, 10))


@pytest.mark.parametrize("duration_minutes", [0, -15])
def test_rejects_non_positive_duration(duration_minutes):
    with pytest.raises(InvalidAppointmentData):
        at("10:00", duration_minutes=duration_minutes)


@pytest.mark.parametrize(
    ("time", "duration_minutes", "expected"),
    [
        ("10:15", 30, True),
        ("09:45", 30, True),
        ("09:00", 120, True),
        ("10:30", 30, False),
        ("09:30", 30, False),
    ],
)
def test_overlaps_only_when_times_intersect(time, duration_minutes, expected):
    booked = at("10:00")

    assert at(time, duration_minutes).overlaps(booked) is expected
    assert booked.overlaps(at(time, duration_minutes)) is expected


def test_conflicts_with_overlapping_appointment_of_same_veterinarian():
    booked = at("10:00")

    with pytest.raises(DoubleBooking, match=VETERINARIAN_BUSY):
        at("10:15", veterinarian_id=booked.veterinarian_id).ensure_no_conflict_with([booked])


def test_conflicts_with_overlapping_appointment_of_same_pet():
    booked = at("10:00")

    with pytest.raises(DoubleBooking, match=PET_BUSY):
        at("10:15", pet_id=booked.pet_id).ensure_no_conflict_with([booked])


def test_ignores_appointments_that_do_not_conflict():
    booked = at("10:00")
    cancelled = at("10:00", veterinarian_id=booked.veterinarian_id, status=AppointmentStatus.CANCELLED)
    back_to_back = at("10:30", veterinarian_id=booked.veterinarian_id)
    other_veterinarian_and_pet = at("10:00")

    booked.ensure_no_conflict_with([booked, cancelled, back_to_back, other_veterinarian_and_pet])


def test_must_start_after_given_moment():
    appointment = at("10:00")

    appointment.ensure_starts_after(datetime(2030, 1, 1, 9, 59, tzinfo=UTC))
    with pytest.raises(InvalidAppointmentData):
        appointment.ensure_starts_after(appointment.starts_at)


def test_cancels_scheduled_appointment_once():
    appointment = at("10:00")

    appointment.cancel()

    assert appointment.status is AppointmentStatus.CANCELLED
    with pytest.raises(AppointmentAlreadyCancelled):
        appointment.cancel()


def test_owner_passes_ownership_check():
    appointment = at("10:00")

    appointment.ensure_owned_by(appointment.owner_id)


def test_other_user_fails_ownership_check():
    with pytest.raises(NotAllowed):
        at("10:00").ensure_owned_by(uuid4())
