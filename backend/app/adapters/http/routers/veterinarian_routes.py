from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import AwareDatetime

from app.adapters.http.dependencies.auth_dependencies import get_current_user
from app.adapters.http.dependencies.veterinarian_dependencies import (
    get_list_available_veterinarians,
    get_list_veterinarians,
)
from app.adapters.http.schemas.appointment_schemas import (
    MAX_DURATION_MINUTES,
    MIN_DURATION_MINUTES,
)
from app.adapters.http.schemas.veterinarian_schemas import VeterinarianResponse
from app.application.use_cases.veterinarians.list_available_veterinarians import (
    ListAvailableVeterinarians,
)
from app.application.use_cases.veterinarians.list_veterinarians import ListVeterinarians

# Every route here requires a logged-in user, checked once at the router level.
router = APIRouter(
    prefix="/veterinarians", tags=["veterinarians"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[VeterinarianResponse])
def list_veterinarians(
    use_case: Annotated[ListVeterinarians, Depends(get_list_veterinarians)],
) -> list[VeterinarianResponse]:
    # List every veterinarian with the hospitals they work at.
    return [VeterinarianResponse.from_domain(v) for v in use_case.execute()]


@router.get("/available", response_model=list[VeterinarianResponse])
def list_available_veterinarians(
    # FastAPI validates the query: a UUID, a timezone-aware datetime and 15 to 240 minutes (422).
    hospital_id: UUID,
    starts_at: AwareDatetime,
    duration_minutes: Annotated[int, Query(ge=MIN_DURATION_MINUTES, le=MAX_DURATION_MINUTES)],
    use_case: Annotated[ListAvailableVeterinarians, Depends(get_list_available_veterinarians)],
) -> list[VeterinarianResponse]:
    """Veterinarians of the hospital with no appointment, at any hospital, during that time."""
    # Find who works at that hospital and is free during that time.
    veterinarians = use_case.execute(
        hospital_id=hospital_id, starts_at=starts_at, duration_minutes=duration_minutes
    )
    return [VeterinarianResponse.from_domain(v) for v in veterinarians]
