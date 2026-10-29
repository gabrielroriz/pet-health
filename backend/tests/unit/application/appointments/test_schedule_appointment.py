from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.adapters.persistence.in_memory.in_memory_appointment_repository import (
    InMemoryAppointmentRepository,
)
from app.adapters.persistence.in_memory.in_memory_hospital_repository import (
    InMemoryHospitalRepository,
)
from app.adapters.persistence.in_memory.in_memory_pet_repository import InMemoryPetRepository
from app.adapters.persistence.in_memory.in_memory_veterinarian_repository import (
    InMemoryVeterinarianRepository,
)
from app.application.use_cases.appointments.schedule_appointment import (
    MAX_ATTEMPTS,
    ScheduleAppointment,
)
from app.domain.appointment import PET_BUSY, VETERINARIAN_BUSY, Appointment, AppointmentStatus
from app.domain.errors import (
    AgendaChanged,
    DoubleBooking,
    HospitalNotFound,
    InvalidAppointmentData,
    NotAllowed,
    PetNotFound,
    VeterinarianNotFound,
)
from app.domain.hospital import Hospital
from app.domain.pet import Pet, Species
from app.domain.veterinarian import Veterinarian


def at(time: str) -> datetime:
    return datetime.fromisoformat(f"2030-01-01T{time}:00+00:00")


class RacingAppointmentRepository(InMemoryAppointmentRepository):
    """Saves each rival right after the overlap check, as a concurrent request could."""

    def __init__(self, rivals: list[Appointment]) -> None:
        super().__init__()
        self.rivals = rivals

    def list_scheduled_overlapping(self, starts_at: datetime, ends_at: datetime) -> list[Appointment]:
        found = super().list_scheduled_overlapping(starts_at, ends_at)
        if self.rivals:
            rival = self.rivals.pop(0)
            self.add(rival, self.agenda_version(rival.veterinarian_id))
        return found


@pytest.fixture
def pets() -> InMemoryPetRepository:
    return InMemoryPetRepository()


@pytest.fixture
def hospitals() -> InMemoryHospitalRepository:
    return InMemoryHospitalRepository()


@pytest.fixture
def veterinarians() -> InMemoryVeterinarianRepository:
    return InMemoryVeterinarianRepository()


@pytest.fixture
def pet(pets) -> Pet:
    pet = Pet(owner_id=uuid4(), name="Thor", species=Species.DOG)
    pets.add(pet)
    return pet


@pytest.fixture
def hospital(hospitals) -> Hospital:
    hospital = Hospital(name="PetCare Downtown")
    hospitals.add(hospital)
    return hospital


@pytest.fixture
def veterinarian(veterinarians, hospital) -> Veterinarian:
    veterinarian = Veterinarian(name="Dr. Beatriz Costa", hospital_ids=frozenset({hospital.id}))
    veterinarians.add(veterinarian)
    return veterinarian


@pytest.fixture
def another_pet(pets, pet) -> Pet:
    another = Pet(owner_id=pet.owner_id, name="Luna", species=Species.CAT)
    pets.add(another)
    return another


@pytest.fixture
def another_veterinarian(veterinarians, hospital) -> Veterinarian:
    another = Veterinarian(name="Dr. Carlos Lima", hospital_ids=frozenset({hospital.id}))
    veterinarians.add(another)
    return another


@pytest.fixture
def make_schedule(pets, hospitals, veterinarians, pet, hospital, veterinarian):
    def make_schedule(appointments: InMemoryAppointmentRepository):
        use_case = ScheduleAppointment(appointments, pets, hospitals, veterinarians)

        def schedule(**overrides) -> Appointment:
            data = {
                "owner_id": pet.owner_id,
                "pet_id": pet.id,
                "hospital_id": hospital.id,
                "veterinarian_id": veterinarian.id,
                "starts_at": at("10:00"),
                "duration_minutes": 30,
                "reason": "Check-up",
            }
            return use_case.execute(**(data | overrides))

        return schedule

    return make_schedule


@pytest.fixture
def appointments() -> InMemoryAppointmentRepository:
    return InMemoryAppointmentRepository()


@pytest.fixture
def schedule(make_schedule, appointments):
    return make_schedule(appointments)


def rival(pet: Pet, hospital: Hospital, veterinarian: Veterinarian, time: str) -> Appointment:
    return Appointment(
        owner_id=pet.owner_id,
        pet_id=pet.id,
        hospital_id=hospital.id,
        veterinarian_id=veterinarian.id,
        starts_at=at(time),
        duration_minutes=30,
        reason="Booked by a concurrent request",
    )


def test_schedules_appointment_and_bumps_agenda_version(schedule, appointments, pet, veterinarian):
    appointment = schedule()

    assert appointment.owner_id == pet.owner_id
    assert appointment.status is AppointmentStatus.SCHEDULED
    assert appointments.get(appointment.id) is appointment
    assert appointments.agenda_version(veterinarian.id) == 1


def test_raises_when_pet_does_not_exist(schedule, appointments):
    with pytest.raises(PetNotFound):
        schedule(pet_id=uuid4())

    assert len(appointments) == 0


def test_raises_when_pet_belongs_to_another_user(schedule):
    with pytest.raises(NotAllowed):
        schedule(owner_id=uuid4())


def test_raises_when_hospital_does_not_exist(schedule):
    with pytest.raises(HospitalNotFound):
        schedule(hospital_id=uuid4())


def test_raises_when_veterinarian_does_not_exist(schedule):
    with pytest.raises(VeterinarianNotFound):
        schedule(veterinarian_id=uuid4())


def test_rejects_veterinarian_of_another_hospital(schedule, hospitals):
    elsewhere = Hospital(name="Happy Paws Clinic")
    hospitals.add(elsewhere)

    with pytest.raises(InvalidAppointmentData):
        schedule(hospital_id=elsewhere.id)


def test_rejects_appointment_in_the_past(schedule):
    with pytest.raises(InvalidAppointmentData):
        schedule(starts_at=datetime.now(UTC) - timedelta(minutes=1))


def test_rejects_overlap_with_same_veterinarian(schedule, appointments, another_pet):
    schedule()

    with pytest.raises(DoubleBooking, match=VETERINARIAN_BUSY):
        schedule(pet_id=another_pet.id, starts_at=at("10:15"))

    assert len(appointments) == 1


def test_rejects_overlap_with_same_pet(schedule, another_veterinarian):
    schedule()

    with pytest.raises(DoubleBooking, match=PET_BUSY):
        schedule(veterinarian_id=another_veterinarian.id, starts_at=at("09:45"))


def test_accepts_back_to_back_appointments(schedule, appointments):
    schedule()
    schedule(starts_at=at("09:30"))
    schedule(starts_at=at("10:30"))

    assert len(appointments) == 3


def test_accepts_same_time_with_another_veterinarian_and_pet(
    schedule, appointments, another_pet, another_veterinarian
):
    schedule()
    schedule(pet_id=another_pet.id, veterinarian_id=another_veterinarian.id)

    assert len(appointments) == 2


def test_retries_when_concurrent_booking_changes_agenda(
    make_schedule, another_pet, hospital, veterinarian
):
    appointments = RacingAppointmentRepository([rival(another_pet, hospital, veterinarian, "14:00")])

    appointment = make_schedule(appointments)()

    assert appointments.get(appointment.id) is appointment
    assert len(appointments) == 2
    assert appointments.agenda_version(veterinarian.id) == 2


def test_rejects_overlap_saved_by_concurrent_booking(make_schedule, another_pet, hospital, veterinarian):
    appointments = RacingAppointmentRepository([rival(another_pet, hospital, veterinarian, "10:15")])

    with pytest.raises(DoubleBooking, match=VETERINARIAN_BUSY):
        make_schedule(appointments)()

    assert len(appointments) == 1


def test_gives_up_when_agenda_keeps_changing(make_schedule, another_pet, hospital, veterinarian):
    rivals = [rival(another_pet, hospital, veterinarian, f"{14 + i}:00") for i in range(MAX_ATTEMPTS)]
    appointments = RacingAppointmentRepository(rivals)

    with pytest.raises(AgendaChanged):
        make_schedule(appointments)()

    assert len(appointments) == MAX_ATTEMPTS


def test_rejects_pet_overlap_that_slips_past_the_check(
    make_schedule, pet, hospital, another_veterinarian
):
    # Another veterinarian's agenda isn't locked, so the overlap is only caught when saving.
    appointments = RacingAppointmentRepository([rival(pet, hospital, another_veterinarian, "10:00")])

    with pytest.raises(DoubleBooking, match=PET_BUSY):
        make_schedule(appointments)()

    assert len(appointments) == 1
