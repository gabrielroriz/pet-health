from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.adapters.http.dependencies import get_authenticate
from app.application.use_cases.authenticate import Authenticate
from app.domain.errors import NotAuthenticated
from app.domain.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    use_case: Annotated[Authenticate, Depends(get_authenticate)],
) -> User:
    if credentials is None:
        raise NotAuthenticated("Missing bearer token.")
    return use_case.execute(credentials.credentials)
