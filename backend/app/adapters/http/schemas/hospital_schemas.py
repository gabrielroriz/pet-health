from typing import Self
from uuid import UUID

from pydantic import BaseModel

from app.domain.hospital import Hospital


class HospitalNetworkResponse(BaseModel):
    id: UUID
    name: str


class HospitalResponse(BaseModel):
    id: UUID
    name: str
    # null for an independent hospital.
    network: HospitalNetworkResponse | None

    @classmethod
    def from_domain(cls, hospital: Hospital) -> Self:
        network = (
            HospitalNetworkResponse(id=hospital.network.id, name=hospital.network.name)
            if hospital.network is not None
            else None
        )
        return cls(id=hospital.id, name=hospital.name, network=network)
