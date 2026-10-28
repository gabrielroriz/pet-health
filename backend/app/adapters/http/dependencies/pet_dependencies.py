from typing import Annotated

from fastapi import Depends, Request

from app.application.ports.repositories.pet_repository import PetRepository
from app.application.use_cases.pets.get_pet import GetPet
from app.application.use_cases.pets.register_pet import RegisterPet


def get_pet_repository(request: Request) -> PetRepository:
    return request.app.state.pets


PetRepositoryDep = Annotated[PetRepository, Depends(get_pet_repository)]


def get_register_pet(pets: PetRepositoryDep) -> RegisterPet:
    return RegisterPet(pets)


def get_get_pet(pets: PetRepositoryDep) -> GetPet:
    return GetPet(pets)
