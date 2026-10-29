from dataclasses import dataclass, field
from uuid import UUID, uuid4


# A group of hospitals; each hospital belongs to at most one network.
@dataclass
class HospitalNetwork:
    name: str
    id: UUID = field(default_factory=uuid4)
