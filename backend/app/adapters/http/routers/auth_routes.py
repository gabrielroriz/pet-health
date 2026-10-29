from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.http.dependencies.auth_dependencies import get_current_user
from app.adapters.http.dependencies.auth_dependencies import get_log_in
from app.adapters.http.schemas.auth_schemas import LoginRequest, TokenResponse, UserResponse
from app.application.use_cases.auth.log_in import LogIn
from app.domain.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def log_in(
    payload: LoginRequest,
    use_case: Annotated[LogIn, Depends(get_log_in)],
) -> TokenResponse:
    """Development login: no password, unknown emails get a new user."""
    # Find or create the user by email and hand back a new bearer token.
    return TokenResponse(access_token=use_case.execute(payload.email))


@router.get("/me", response_model=UserResponse)
def read_me(user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    # get_current_user already turned the token into a user.
    return UserResponse.from_domain(user)
