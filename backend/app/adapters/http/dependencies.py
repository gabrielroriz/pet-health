from typing import Annotated

from fastapi import Depends, Request

from app.application.ports import PetRepository, TokenService, UserRepository
from app.application.use_cases.authenticate import Authenticate
from app.application.use_cases.get_pet import GetPet
from app.application.use_cases.log_in import LogIn
from app.application.use_cases.register_pet import RegisterPet


def get_pet_repository(request: Request) -> PetRepository:
    return request.app.state.pets


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.users


def get_token_service(request: Request) -> TokenService:
    return request.app.state.tokens


PetRepositoryDep = Annotated[PetRepository, Depends(get_pet_repository)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


def get_register_pet(pets: PetRepositoryDep) -> RegisterPet:
    return RegisterPet(pets)


def get_get_pet(pets: PetRepositoryDep) -> GetPet:
    return GetPet(pets)


def get_log_in(users: UserRepositoryDep, tokens: TokenServiceDep) -> LogIn:
    return LogIn(users, tokens)


def get_authenticate(users: UserRepositoryDep, tokens: TokenServiceDep) -> Authenticate:
    return Authenticate(users, tokens)
