from app.application.ports.repositories.hospital_repository import HospitalRepository
from app.domain.hospital import Hospital


class ListHospitals:
    def __init__(self, hospitals: HospitalRepository) -> None:
        self.hospitals = hospitals

    def execute(self) -> list[Hospital]:
        # Every hospital with its network, sorted by name.
        return self.hospitals.list_all()
