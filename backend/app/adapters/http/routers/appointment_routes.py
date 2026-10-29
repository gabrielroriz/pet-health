from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.adapters.http.dependencies.appointment_dependencies import (
    get_cancel_appointment,
    get_list_appointments,
    get_schedule_appointment,
)
from app.adapters.http.dependencies.auth_dependencies import get_current_user
from app.adapters.http.schemas.appointment_schemas import (
    AppointmentResponse,
    ScheduleAppointmentRequest,
)
from app.application.use_cases.appointments.cancel_appointment import CancelAppointment
from app.application.use_cases.appointments.list_appointments import ListAppointments
from app.application.use_cases.appointments.schedule_appointment import ScheduleAppointment
from app.domain.user import User

# Every route below takes the logged-in user from get_current_user (401 without a token).
router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=list[AppointmentResponse])
def list_appointments(
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ListAppointments, Depends(get_list_appointments)],
) -> list[AppointmentResponse]:
    """Scheduled appointments of the logged-in user, earliest first."""
    # List the user's appointments and map each one to JSON.
    return [AppointmentResponse.from_domain(a) for a in use_case.execute(owner_id=user.id)]


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def schedule_appointment(
    payload: ScheduleAppointmentRequest,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ScheduleAppointment, Depends(get_schedule_appointment)],
) -> AppointmentResponse:
    """Returns 409 if the veterinarian or the pet already has an appointment at that time."""
    # FastAPI already validated the body (422); the use case applies the business rules, double booking included.
    appointment = use_case.execute(owner_id=user.id, **payload.model_dump())
    return AppointmentResponse.from_domain(appointment)


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: UUID,
    user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[CancelAppointment, Depends(get_cancel_appointment)],
) -> AppointmentResponse:
    """Cancels the appointment and frees its time for other bookings."""
    # Cancel as the logged-in user; domain errors become 403/404/409 in error_handlers.py.
    appointment = use_case.execute(user_id=user.id, appointment_id=appointment_id)
    return AppointmentResponse.from_domain(appointment)
