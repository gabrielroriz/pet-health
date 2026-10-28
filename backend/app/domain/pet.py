from dataclasses import dataclass, field
from datetime import date
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.errors import InvalidPetData, NotAllowed

class Species(StrEnum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    RABBIT = "rabbit"
    OTHER = "other"

@dataclass
class Pet:
    owner_id: UUID
    name: str
    species: Species
    birth_date: date | None = None
    breed: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise InvalidPetData("Name must not be blank.")
        if self.birth_date is not None and self.birth_date > date.today():
            raise InvalidPetData("Birth date must not be in the future.")
        if self.breed is not None:
            self.breed = self.breed.strip() or None

    def ensure_owned_by(self, user_id: UUID) -> None:
        if self.owner_id != user_id:
            raise NotAllowed("This pet belongs to another user.")
