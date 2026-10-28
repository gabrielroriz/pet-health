from datetime import date, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.adapters.http.auth import PLACEHOLDER_USER
from app.domain.pet import Pet, Species
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def register(client: TestClient, **overrides):
    return client.post("/pets", json={"name": "Rex", "species": "dog"} | overrides)


def test_registers_pet(client):
    response = register(client, birth_date="2020-05-01", breed="Beagle")

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Rex"
    assert body["species"] == "dog"
    assert body["birth_date"] == "2020-05-01"
    assert body["breed"] == "Beagle"
    assert body["owner_id"] == str(PLACEHOLDER_USER.id)


def test_gets_registered_pet(client):
    pet_id = register(client).json()["id"]

    response = client.get(f"/pets/{pet_id}")

    assert response.status_code == 200
    assert response.json()["id"] == pet_id


@pytest.mark.parametrize(
    "payload",
    [
        {"species": "dog"},
        {"name": "Rex", "species": "dragon"},
        {"name": "", "species": "dog"},
        {"name": "Rex", "species": "dog", "birth_date": "not-a-date"},
        {"name": "Rex", "species": "dog", "color": "brown"},
    ],
)
def test_rejects_invalid_payload(client, payload):
    assert client.post("/pets", json=payload).status_code == 422


def test_rejects_pet_breaking_domain_rules(client):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    response = register(client, birth_date=tomorrow)

    assert response.status_code == 422
    assert response.json() == {"detail": "Birth date must not be in the future."}


def test_returns_404_for_unknown_pet(client):
    assert client.get(f"/pets/{uuid4()}").status_code == 404


def test_returns_422_for_malformed_pet_id(client):
    assert client.get("/pets/not-a-uuid").status_code == 422


def test_returns_403_for_another_users_pet(client):
    pet = Pet(owner_id=uuid4(), name="Mia", species=Species.CAT)
    client.app.state.pets.add(pet)

    assert client.get(f"/pets/{pet.id}").status_code == 403
