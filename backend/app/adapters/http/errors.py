from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.errors import (
    DomainError,
    InvalidPetData,
    InvalidUserData,
    NotAllowed,
    NotAuthenticated,
    PetNotFound,
)

STATUS_CODES: dict[type[DomainError], int] = {
    PetNotFound: status.HTTP_404_NOT_FOUND,
    NotAuthenticated: status.HTTP_401_UNAUTHORIZED,
    NotAllowed: status.HTTP_403_FORBIDDEN,
    InvalidPetData: status.HTTP_422_UNPROCESSABLE_CONTENT,
    InvalidUserData: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    status_code = next(
        (STATUS_CODES[cls] for cls in type(exc).__mro__ if cls in STATUS_CODES),
        status.HTTP_400_BAD_REQUEST,
    )
    headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
    return JSONResponse(
        status_code=status_code, content={"detail": str(exc)}, headers=headers
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, handle_domain_error)
