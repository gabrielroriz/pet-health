from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.adapters.http.dependencies.persistence_dependencies import UserRepositoryDep
from app.application.ports.services.token_service import TokenService
from app.application.use_cases.auth.authenticate import Authenticate
from app.application.use_cases.auth.log_in import LogIn
from app.domain.errors import NotAuthenticated
from app.domain.user import User


def get_token_service(request: Request) -> TokenService:
    # The single in-memory token store created in main.py.
    return request.app.state.tokens


TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]


# FastAPI calls these per request to build each use case with its repositories.
def get_log_in(users: UserRepositoryDep, tokens: TokenServiceDep) -> LogIn:
    return LogIn(users, tokens)


def get_authenticate(users: UserRepositoryDep, tokens: TokenServiceDep) -> Authenticate:
    return Authenticate(users, tokens)


# Reads the 'Authorization: Bearer <token>' header; we raise our own 401 when it's missing.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    use_case: Annotated[Authenticate, Depends(get_authenticate)],
) -> User:
    # Every protected route depends on this: no token means 401.
    if credentials is None:
        raise NotAuthenticated("Missing bearer token.")
    # Turn the token into the logged-in User, or 401 if it's invalid.
    return use_case.execute(credentials.credentials)
