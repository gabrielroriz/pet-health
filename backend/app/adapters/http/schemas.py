from datetime import date
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.pet import Pet, Species


class RegisterPetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    species: Species
    birth_date: date | None = None
    breed: str | None = Field(default=None, max_length=100)


class PetResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    species: Species
    birth_date: date | None
    breed: str | None

    @classmethod
    def from_domain(cls, pet: Pet) -> Self:
        return cls(
            id=pet.id,
            owner_id=pet.owner_id,
            name=pet.name,
            species=pet.species,
            birth_date=pet.birth_date,
            breed=pet.breed,
        )
