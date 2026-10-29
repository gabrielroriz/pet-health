from app.adapters.http.dependencies.persistence_dependencies import (
    AppointmentRepositoryDep,
    HospitalRepositoryDep,
    PetRepositoryDep,
    VeterinarianRepositoryDep,
)
from app.application.use_cases.appointments.cancel_appointment import CancelAppointment
from app.application.use_cases.appointments.list_appointments import ListAppointments
from app.application.use_cases.appointments.schedule_appointment import ScheduleAppointment


# FastAPI calls these per request to build each use case with its repositories.
def get_schedule_appointment(
    appointments: AppointmentRepositoryDep,
    pets: PetRepositoryDep,
    hospitals: HospitalRepositoryDep,
    veterinarians: VeterinarianRepositoryDep,
) -> ScheduleAppointment:
    return ScheduleAppointment(appointments, pets, hospitals, veterinarians)


def get_list_appointments(appointments: AppointmentRepositoryDep) -> ListAppointments:
    return ListAppointments(appointments)


def get_cancel_appointment(appointments: AppointmentRepositoryDep) -> CancelAppointment:
    return CancelAppointment(appointments)
