from app.adapters.http.dependencies.persistence_dependencies import HospitalRepositoryDep
from app.application.use_cases.hospitals.list_hospitals import ListHospitals


# FastAPI calls these per request to build each use case with its repositories.
def get_list_hospitals(hospitals: HospitalRepositoryDep) -> ListHospitals:
    return ListHospitals(hospitals)
