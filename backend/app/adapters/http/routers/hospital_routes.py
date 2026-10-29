from typing import Annotated

from fastapi import APIRouter, Depends

from app.adapters.http.dependencies.auth_dependencies import get_current_user
from app.adapters.http.dependencies.hospital_dependencies import get_list_hospitals
from app.adapters.http.schemas.hospital_schemas import HospitalResponse
from app.application.use_cases.hospitals.list_hospitals import ListHospitals

# Every route here requires a logged-in user, checked once at the router level.
router = APIRouter(
    prefix="/hospitals", tags=["hospitals"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[HospitalResponse])
def list_hospitals(
    use_case: Annotated[ListHospitals, Depends(get_list_hospitals)],
) -> list[HospitalResponse]:
    # List the hospitals and map each one, with its network, to JSON.
    return [HospitalResponse.from_domain(h) for h in use_case.execute()]
