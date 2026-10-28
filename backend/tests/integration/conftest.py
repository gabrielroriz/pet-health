import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def log_in(client: TestClient, email: str = "ana@example.com") -> dict[str, str]:
    token = client.post("/auth/login", json={"email": email}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    return log_in(client)
