from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.ports.services.token_service import TokenService
from app.application.ports.repositories.user_repository import UserRepository
from app.application.use_cases.auth.authenticate import Authenticate
from app.application.use_cases.auth.log_in import LogIn
from app.domain.errors import NotAuthenticated
from app.domain.user import User


def get_user_repository(request: Request) -> UserRepository:
    return request.app.state.users


def get_token_service(request: Request) -> TokenService:
    return request.app.state.tokens


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


def get_log_in(users: UserRepositoryDep, tokens: TokenServiceDep) -> LogIn:
    return LogIn(users, tokens)


def get_authenticate(users: UserRepositoryDep, tokens: TokenServiceDep) -> Authenticate:
    return Authenticate(users, tokens)


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    use_case: Annotated[Authenticate, Depends(get_authenticate)],
) -> User:
    if credentials is None:
        raise NotAuthenticated("Missing bearer token.")
    return use_case.execute(credentials.credentials)
