from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.adapters.http.dependencies.auth_dependencies import get_current_user
from app.adapters.http.dependencies.pet_dependencies import (
    get_get_pet,
    get_list_pets,
    get_register_pet,
)
from app.adapters.http.schemas.pet_schemas import PetResponse, RegisterPetRequest
from app.application.use_cases.pets.get_pet import GetPet
from app.application.use_cases.pets.list_pets import ListPets
from app.application.use_cases.pets.register_pet import RegisterPet
from app.domain.user import User

router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("", response_model=list[PetResponse])
def list_pets(
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListPets, Depends(get_list_pets)],
) -> list[PetResponse]:
    # List the logged-in user's pets, to pick one when booking.
    return [PetResponse.from_domain(pet) for pet in use_case.execute(owner_id=user.id)]


@router.post("", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def register_pet(
    payload: RegisterPetRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[RegisterPet, Depends(get_register_pet)],
) -> PetResponse:
    # The logged-in user becomes the pet's owner.
    pet = use_case.execute(owner_id=user.id, **payload.model_dump())
    return PetResponse.from_domain(pet)


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(
    pet_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetPet, Depends(get_get_pet)],
) -> PetResponse:
    # 404 if the pet doesn't exist, 403 if it belongs to someone else.
    pet = use_case.execute(user_id=user.id, pet_id=pet_id)
    return PetResponse.from_domain(pet)
