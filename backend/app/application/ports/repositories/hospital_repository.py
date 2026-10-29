from typing import Protocol
from uuid import UUID

from app.domain.hospital import Hospital


# Read-only for use cases: hospitals come from the seed for now.
class HospitalRepository(Protocol):
    def get(self, hospital_id: UUID) -> Hospital | None: ...

    def list_all(self) -> list[Hospital]: ...
