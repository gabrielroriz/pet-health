from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.errors import (
    AgendaChanged,
    AppointmentAlreadyCancelled,
    AppointmentNotFound,
    DomainError,
    DoubleBooking,
    HospitalNotFound,
    InvalidAppointmentData,
    InvalidPetData,
    InvalidUserData,
    NotAllowed,
    NotAuthenticated,
    PetNotFound,
    VeterinarianNotFound,
)

# Which HTTP status each domain error becomes; anything unlisted falls back to 400.
STATUS_CODES: dict[type[DomainError], int] = {
    PetNotFound: status.HTTP_404_NOT_FOUND,
    AppointmentNotFound: status.HTTP_404_NOT_FOUND,
    HospitalNotFound: status.HTTP_404_NOT_FOUND,
    VeterinarianNotFound: status.HTTP_404_NOT_FOUND,
    NotAuthenticated: status.HTTP_401_UNAUTHORIZED,
    NotAllowed: status.HTTP_403_FORBIDDEN,
    DoubleBooking: status.HTTP_409_CONFLICT,
    AgendaChanged: status.HTTP_409_CONFLICT,
    AppointmentAlreadyCancelled: status.HTTP_409_CONFLICT,
    InvalidPetData: status.HTTP_422_UNPROCESSABLE_CONTENT,
    InvalidUserData: status.HTTP_422_UNPROCESSABLE_CONTENT,
    InvalidAppointmentData: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    # Use the closest mapped class, so subclasses inherit their parent's status.
    status_code = next(
        (STATUS_CODES[cls] for cls in type(exc).__mro__ if cls in STATUS_CODES),
        status.HTTP_400_BAD_REQUEST,
    )
    # 401 responses tell the client to send a bearer token.
    headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
    # The error's message becomes the response's 'detail'.
    return JSONResponse(
        status_code=status_code, content={"detail": str(exc)}, headers=headers
    )


def register_error_handlers(app: FastAPI) -> None:
    # Every DomainError raised in a route or use case ends up in handle_domain_error.
    app.add_exception_handler(DomainError, handle_domain_error)
