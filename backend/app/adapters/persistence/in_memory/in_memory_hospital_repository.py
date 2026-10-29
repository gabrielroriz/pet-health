from uuid import UUID

from app.domain.hospital import Hospital


class InMemoryHospitalRepository:
    def __init__(self) -> None:
        self._hospitals: dict[UUID, Hospital] = {}

    def __len__(self) -> int:
        return len(self._hospitals)

    def add(self, hospital: Hospital) -> None:
        self._hospitals[hospital.id] = hospital

    def get(self, hospital_id: UUID) -> Hospital | None:
        return self._hospitals.get(hospital_id)

    def list_all(self) -> list[Hospital]:
        # Sorted by name, like the SQL repository.
        return sorted(self._hospitals.values(), key=lambda h: h.name)
