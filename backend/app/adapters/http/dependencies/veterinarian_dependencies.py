from app.adapters.http.dependencies.persistence_dependencies import (
    AppointmentRepositoryDep,
    HospitalRepositoryDep,
    VeterinarianRepositoryDep,
)
from app.application.use_cases.veterinarians.list_available_veterinarians import (
    ListAvailableVeterinarians,
)
from app.application.use_cases.veterinarians.list_veterinarians import ListVeterinarians


# FastAPI calls these per request to build each use case with its repositories.
def get_list_veterinarians(veterinarians: VeterinarianRepositoryDep) -> ListVeterinarians:
    return ListVeterinarians(veterinarians)


def get_list_available_veterinarians(
    appointments: AppointmentRepositoryDep,
    hospitals: HospitalRepositoryDep,
    veterinarians: VeterinarianRepositoryDep,
) -> ListAvailableVeterinarians:
    return ListAvailableVeterinarians(appointments, hospitals, veterinarians)
