from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.adapters.http.auth import get_current_user
from app.adapters.http.dependencies import get_get_pet, get_register_pet
from app.adapters.http.schemas import PetResponse, RegisterPetRequest
from app.application.use_cases.get_pet import GetPet
from app.application.use_cases.register_pet import RegisterPet
from app.domain.user import User

router = APIRouter(prefix="/pets", tags=["pets"])


@router.post("", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def register_pet(
    payload: RegisterPetRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[RegisterPet, Depends(get_register_pet)],
) -> PetResponse:
    pet = use_case.execute(owner_id=user.id, **payload.model_dump())
    return PetResponse.from_domain(pet)


@router.get("/{pet_id}", response_model=PetResponse)
def get_pet(
    pet_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetPet, Depends(get_get_pet)],
) -> PetResponse:
    pet = use_case.execute(user_id=user.id, pet_id=pet_id)
    return PetResponse.from_domain(pet)
