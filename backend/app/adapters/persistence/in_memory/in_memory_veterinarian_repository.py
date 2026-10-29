from uuid import UUID

from app.domain.veterinarian import Veterinarian


class InMemoryVeterinarianRepository:
    def __init__(self) -> None:
        self._veterinarians: dict[UUID, Veterinarian] = {}

    def __len__(self) -> int:
        return len(self._veterinarians)

    def add(self, veterinarian: Veterinarian) -> None:
        self._veterinarians[veterinarian.id] = veterinarian

    def get(self, veterinarian_id: UUID) -> Veterinarian | None:
        return self._veterinarians.get(veterinarian_id)

    def list_all(self) -> list[Veterinarian]:
        # Sorted by name, like the SQL repository.
        return sorted(self._veterinarians.values(), key=lambda v: v.name)

    def list_by_hospital(self, hospital_id: UUID) -> list[Veterinarian]:
        # Veterinarians whose hospitals include this one.
        return [v for v in self.list_all() if hospital_id in v.hospital_ids]
