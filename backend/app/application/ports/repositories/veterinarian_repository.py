from typing import Protocol
from uuid import UUID

from app.domain.veterinarian import Veterinarian


# Read-only for use cases: veterinarians come from the seed for now.
class VeterinarianRepository(Protocol):
    def get(self, veterinarian_id: UUID) -> Veterinarian | None: ...

    def list_all(self) -> list[Veterinarian]: ...

    # Veterinarians who work at the given hospital.
    def list_by_hospital(self, hospital_id: UUID) -> list[Veterinarian]: ...
