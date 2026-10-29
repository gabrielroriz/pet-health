from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.hospital_network import HospitalNetwork


@dataclass
class Hospital:
    name: str
    # None for an independent hospital; a hospital is in at most one network.
    network: HospitalNetwork | None = None
    id: UUID = field(default_factory=uuid4)
