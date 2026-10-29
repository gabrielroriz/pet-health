from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.errors import InvalidAppointmentData


@dataclass
class Veterinarian:
    name: str
    # Every hospital where the veterinarian takes appointments.
    hospital_ids: frozenset[UUID] = frozenset()
    id: UUID = field(default_factory=uuid4)

    def ensure_works_at(self, hospital_id: UUID) -> None:
        # Booking a veterinarian at a hospital they don't work at is rejected (422).
        if hospital_id not in self.hospital_ids:
            raise InvalidAppointmentData("The veterinarian doesn't work at this hospital.")
