from datetime import date
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.pet import Pet, Species
from app.domain.user import User


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


class LoginRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str

    @classmethod
    def from_domain(cls, user: User) -> Self:
        return cls(id=user.id, email=user.email)
