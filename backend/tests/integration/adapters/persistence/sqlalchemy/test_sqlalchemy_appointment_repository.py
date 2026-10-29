from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Barrier

import pytest
from sqlalchemy.exc import IntegrityError

from app.adapters.persistence.sqlalchemy.sqlalchemy_appointment_repository import (
    SqlAlchemyAppointmentRepository,
)
from app.adapters.persistence.sqlalchemy.sqlalchemy_hospital_repository import (
    SqlAlchemyHospitalRepository,
)
from app.adapters.persistence.sqlalchemy.sqlalchemy_pet_repository import SqlAlchemyPetRepository
from app.adapters.persistence.sqlalchemy.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.adapters.persistence.sqlalchemy.sqlalchemy_veterinarian_repository import (
    SqlAlchemyVeterinarianRepository,
)
from app.application.use_cases.appointments.schedule_appointment import (
    MAX_ATTEMPTS,
    ScheduleAppointment,
)
from app.domain.appointment import PET_BUSY, VETERINARIAN_BUSY, Appointment
from app.domain.errors import AgendaChanged, DoubleBooking
from app.domain.hospital import Hospital
from app.domain.pet import Pet, Species
from app.domain.user import User
from app.domain.veterinarian import Veterinarian
from tests.integration.conftest import add_hospital, add_veterinarian


def at(time: str) -> datetime:
    return datetime.fromisoformat(f"2030-01-01T{time}:00+00:00")


@pytest.fixture
def appointments(session) -> SqlAlchemyAppointmentRepository:
    return SqlAlchemyAppointmentRepository(session)


@pytest.fixture
def owner(session) -> User:
    user = User(email="ana@example.com")
    SqlAlchemyUserRepository(session).add(user)
    return user


def adopt(session, owner: User, name: str) -> Pet:
    pet = Pet(owner_id=owner.id, name=name, species=Species.DOG)
    SqlAlchemyPetRepository(session).add(pet)
    return pet


@pytest.fixture
def thor(session, owner) -> Pet:
    return adopt(session, owner, "Thor")


@pytest.fixture
def luna(session, owner) -> Pet:
    return adopt(session, owner, "Luna")


@pytest.fixture
def downtown(session) -> Hospital:
    return add_hospital(session)


@pytest.fixture
def beatriz(session, downtown) -> Veterinarian:
    return add_veterinarian(session, downtown)


@pytest.fixture
def carlos(session, downtown) -> Veterinarian:
    return add_veterinarian(session, downtown, name="Dr. Carlos Lima")


def make(pet: Pet, veterinarian: Veterinarian, hospital: Hospital, time: str) -> Appointment:
    return Appointment(
        owner_id=pet.owner_id,
        pet_id=pet.id,
        hospital_id=hospital.id,
        veterinarian_id=veterinarian.id,
        starts_at=at(time),
        duration_minutes=30,
        reason="Check-up",
    )


def book(appointments, appointment: Appointment) -> Appointment:
    appointments.add(appointment, appointments.agenda_version(appointment.veterinarian_id))
    return appointment


def test_saves_appointment_and_bumps_agenda_version(appointments, thor, downtown, beatriz):
    appointment = make(thor, beatriz, downtown, "10:00")

    appointments.add(appointment, agenda_version=0)

    assert appointments.get(appointment.id) == appointment
    assert appointments.agenda_version(beatriz.id) == 1


def test_rejects_stale_agenda_version(appointments, thor, luna, downtown, beatriz):
    appointments.add(make(thor, beatriz, downtown, "10:00"), agenda_version=0)

    with pytest.raises(AgendaChanged):
        appointments.add(make(luna, beatriz, downtown, "14:00"), agenda_version=0)

    assert len(appointments.list_scheduled_by_owner(thor.owner_id)) == 1
    assert appointments.agenda_version(beatriz.id) == 1


def test_database_rejects_overlap_for_same_veterinarian(appointments, thor, luna, downtown, beatriz):
    book(appointments, make(thor, beatriz, downtown, "10:00"))

    # A current version passes the optimistic lock, so only the constraint stops it.
    with pytest.raises(DoubleBooking, match=VETERINARIAN_BUSY):
        book(appointments, make(luna, beatriz, downtown, "10:15"))

    assert appointments.agenda_version(beatriz.id) == 1


def test_database_rejects_overlap_for_same_pet(appointments, thor, downtown, beatriz, carlos):
    book(appointments, make(thor, beatriz, downtown, "10:00"))

    with pytest.raises(DoubleBooking, match=PET_BUSY):
        book(appointments, make(thor, carlos, downtown, "09:45"))


def test_database_accepts_back_to_back_appointments(appointments, thor, downtown, beatriz):
    book(appointments, make(thor, beatriz, downtown, "10:00"))
    book(appointments, make(thor, beatriz, downtown, "09:30"))
    book(appointments, make(thor, beatriz, downtown, "10:30"))

    assert len(appointments.list_scheduled_by_owner(thor.owner_id)) == 3


def test_cancelled_appointment_frees_its_time(appointments, thor, downtown, beatriz):
    cancelled = book(appointments, make(thor, beatriz, downtown, "10:00"))
    cancelled.cancel()
    appointments.update(cancelled)

    rebooked = book(appointments, make(thor, beatriz, downtown, "10:00"))

    assert appointments.get(cancelled.id) == cancelled
    assert appointments.list_scheduled_by_owner(thor.owner_id) == [rebooked]


def test_database_rejects_veterinarian_of_another_hospital(session, appointments, thor, downtown):
    elsewhere = add_veterinarian(session, add_hospital(session, name="Happy Paws Clinic"))

    with pytest.raises(IntegrityError):
        book(appointments, make(thor, elsewhere, downtown, "10:00"))


def test_lists_scheduled_appointments(appointments, owner, thor, luna, downtown, beatriz, carlos):
    later = book(appointments, make(thor, beatriz, downtown, "15:00"))
    earlier = book(appointments, make(luna, carlos, downtown, "09:00"))
    overlapping = book(appointments, make(thor, carlos, downtown, "10:15"))

    assert appointments.list_scheduled_by_owner(owner.id) == [earlier, overlapping, later]
    assert appointments.list_scheduled_overlapping(at("10:00"), at("10:30")) == [overlapping]
    assert appointments.list_scheduled_overlapping(at("09:30"), at("10:15")) == []


def schedule_concurrently(session_factory, requests: list[dict]) -> list[str]:
    barrier = Barrier(len(requests))

    def schedule(request: dict) -> str:
        with session_factory() as session:
            use_case = ScheduleAppointment(
                SqlAlchemyAppointmentRepository(session),
                SqlAlchemyPetRepository(session),
                SqlAlchemyHospitalRepository(session),
                SqlAlchemyVeterinarianRepository(session),
            )
            barrier.wait()
            try:
                use_case.execute(**request)
            except DoubleBooking:
                return "double booking"
            return "booked"

    with ThreadPoolExecutor(len(requests)) as pool:
        return list(pool.map(schedule, requests))


def request_for(pet: Pet, hospital: Hospital, veterinarian: Veterinarian, time: str) -> dict:
    return {
        "owner_id": pet.owner_id,
        "pet_id": pet.id,
        "hospital_id": hospital.id,
        "veterinarian_id": veterinarian.id,
        "starts_at": at(time),
        "duration_minutes": 30,
        "reason": "Check-up",
    }


def test_only_one_concurrent_booking_for_same_time_wins(session_factory, session, owner, downtown, beatriz):
    pets = [adopt(session, owner, f"Pet {i}") for i in range(5)]

    results = schedule_concurrently(
        session_factory, [request_for(pet, downtown, beatriz, "10:00") for pet in pets]
    )

    assert sorted(results) == ["booked"] + ["double booking"] * 4
    assert len(SqlAlchemyAppointmentRepository(session).list_scheduled_by_owner(owner.id)) == 1


def test_concurrent_bookings_at_different_times_all_go_through(
    session_factory, session, thor, downtown, beatriz
):
    times = [f"{10 + i}:00" for i in range(MAX_ATTEMPTS)]

    results = schedule_concurrently(
        session_factory, [request_for(thor, downtown, beatriz, time) for time in times]
    )

    assert results == ["booked"] * MAX_ATTEMPTS
    assert SqlAlchemyAppointmentRepository(session).agenda_version(beatriz.id) == MAX_ATTEMPTS
