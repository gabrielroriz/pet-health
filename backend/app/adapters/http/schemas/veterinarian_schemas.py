from typing import Self
from uuid import UUID

from pydantic import BaseModel

from app.domain.veterinarian import Veterinarian


class VeterinarianResponse(BaseModel):
    id: UUID
    name: str
    # Lets the client show or filter veterinarians by hospital.
    hospital_ids: list[UUID]

    @classmethod
    def from_domain(cls, veterinarian: Veterinarian) -> Self:
        return cls(
            id=veterinarian.id,
            name=veterinarian.name,
            hospital_ids=sorted(veterinarian.hospital_ids),
        )
