from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.adapters.persistence.sqlalchemy.sqlalchemy_appointment_repository import (
    SqlAlchemyAppointmentRepository,
)
from app.adapters.persistence.sqlalchemy.sqlalchemy_hospital_repository import (
    SqlAlchemyHospitalRepository,
)
from app.adapters.persistence.sqlalchemy.sqlalchemy_pet_repository import SqlAlchemyPetRepository
from app.adapters.persistence.sqlalchemy.sqlalchemy_user_repository import SqlAlchemyUserRepository
from app.adapters.persistence.sqlalchemy.sqlalchemy_veterinarian_repository import (
    SqlAlchemyVeterinarianRepository,
)
from app.application.ports.repositories.appointment_repository import AppointmentRepository
from app.application.ports.repositories.hospital_repository import HospitalRepository
from app.application.ports.repositories.pet_repository import PetRepository
from app.application.ports.repositories.user_repository import UserRepository
from app.application.ports.repositories.veterinarian_repository import VeterinarianRepository


# One session per request, shared by every repository the request uses.
def get_session(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        # The route runs here; closing the session afterwards rolls back anything left uncommitted.
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# Each repository wraps the request's session; swap these classes to change the database.
def get_user_repository(session: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_pet_repository(session: SessionDep) -> PetRepository:
    return SqlAlchemyPetRepository(session)


def get_appointment_repository(session: SessionDep) -> AppointmentRepository:
    return SqlAlchemyAppointmentRepository(session)


def get_hospital_repository(session: SessionDep) -> HospitalRepository:
    return SqlAlchemyHospitalRepository(session)


def get_veterinarian_repository(session: SessionDep) -> VeterinarianRepository:
    return SqlAlchemyVeterinarianRepository(session)


# Shortcuts that let use case factories ask for a repository by its port type.
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
PetRepositoryDep = Annotated[PetRepository, Depends(get_pet_repository)]
AppointmentRepositoryDep = Annotated[AppointmentRepository, Depends(get_appointment_repository)]
HospitalRepositoryDep = Annotated[HospitalRepository, Depends(get_hospital_repository)]
VeterinarianRepositoryDep = Annotated[VeterinarianRepository, Depends(get_veterinarian_repository)]
