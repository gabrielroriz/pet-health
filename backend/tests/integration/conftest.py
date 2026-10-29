from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, make_url, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.persistence.sqlalchemy.sqlalchemy_hospital_repository import (
    SqlAlchemyHospitalRepository,
)
from app.adapters.persistence.sqlalchemy.sqlalchemy_session import create_session_factory
from app.adapters.persistence.sqlalchemy.sqlalchemy_tables import metadata
from app.adapters.persistence.sqlalchemy.sqlalchemy_veterinarian_repository import (
    SqlAlchemyVeterinarianRepository,
)
from app.config import settings
from app.domain.hospital import Hospital
from app.domain.hospital_network import HospitalNetwork
from app.domain.veterinarian import Veterinarian
from app.main import create_app

BACKEND_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def database_url() -> str:
    """A "<name>_test" database on the DATABASE_URL server, migrated to the latest schema."""
    url = make_url(settings.database_url)
    test_url = url.set(database=f"{url.database}_test")
    server = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with server.connect() as connection:
            exists = connection.scalar(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": test_url.database},
            )
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{test_url.database}"'))
    except OperationalError as error:
        pytest.fail(
            f"Integration tests need PostgreSQL at {url.render_as_string()}. "
            f"Start it with `docker compose up -d db`.\n{error.orig}"
        )
    finally:
        server.dispose()

    rendered = test_url.render_as_string(hide_password=False)
    config = Config(BACKEND_DIR / "alembic.ini")
    config.attributes["database_url"] = rendered
    command.upgrade(config, "head")
    return rendered


@pytest.fixture(scope="session")
def engine_session_factory(database_url: str) -> Iterator[sessionmaker[Session]]:
    factory = create_session_factory(database_url)
    yield factory
    factory.kw["bind"].dispose()


@pytest.fixture
def session_factory(engine_session_factory: sessionmaker[Session]) -> sessionmaker[Session]:
    """Empties every table before the test."""
    with engine_session_factory() as session:
        tables = ", ".join(table.name for table in metadata.sorted_tables)
        session.execute(text(f"TRUNCATE {tables} CASCADE"))
        session.commit()
    return engine_session_factory


@pytest.fixture
def session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> TestClient:
    return TestClient(create_app(session_factory))


def log_in(client: TestClient, email: str = "ana@example.com") -> dict[str, str]:
    token = client.post("/auth/login", json={"email": email}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    return log_in(client)


def add_hospital(
    session: Session, name: str = "PetCare Downtown", network: HospitalNetwork | None = None
) -> Hospital:
    hospital = Hospital(name=name, network=network)
    SqlAlchemyHospitalRepository(session).add(hospital)
    return hospital


def add_veterinarian(
    session: Session, *hospitals: Hospital, name: str = "Dr. Beatriz Costa"
) -> Veterinarian:
    veterinarian = Veterinarian(name=name, hospital_ids=frozenset(h.id for h in hospitals))
    SqlAlchemyVeterinarianRepository(session).add(veterinarian)
    return veterinarian
