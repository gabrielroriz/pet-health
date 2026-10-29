from datetime import date, timedelta
from uuid import uuid4

import pytest

from tests.integration.conftest import log_in


def register(client, headers, **overrides):
    payload = {"name": "Rex", "species": "dog"} | overrides
    return client.post("/pets", json=payload, headers=headers)


def test_registers_pet_for_logged_in_user(client, auth_headers):
    response = register(client, auth_headers, birth_date="2020-05-01", breed="Beagle")

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Rex"
    assert body["species"] == "dog"
    assert body["birth_date"] == "2020-05-01"
    assert body["breed"] == "Beagle"
    me = client.get("/auth/me", headers=auth_headers).json()
    assert body["owner_id"] == me["id"]


def test_gets_registered_pet(client, auth_headers):
    pet_id = register(client, auth_headers).json()["id"]

    response = client.get(f"/pets/{pet_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == pet_id


def test_lists_pets_of_logged_in_user_by_name(client, auth_headers):
    register(client, auth_headers, name="Thor")
    register(client, auth_headers, name="Luna", species="cat")
    register(client, log_in(client, "bob@example.com"), name="Rex")

    response = client.get("/pets", headers=auth_headers)

    assert response.status_code == 200
    assert [pet["name"] for pet in response.json()] == ["Luna", "Thor"]


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
def test_rejects_invalid_payload(client, auth_headers, payload):
    assert client.post("/pets", json=payload, headers=auth_headers).status_code == 422


def test_rejects_pet_breaking_domain_rules(client, auth_headers):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    response = register(client, auth_headers, birth_date=tomorrow)

    assert response.status_code == 422
    assert response.json() == {"detail": "Birth date must not be in the future."}


def test_returns_404_for_unknown_pet(client, auth_headers):
    assert client.get(f"/pets/{uuid4()}", headers=auth_headers).status_code == 404


def test_returns_422_for_malformed_pet_id(client, auth_headers):
    assert client.get("/pets/not-a-uuid", headers=auth_headers).status_code == 422


def test_returns_403_for_another_users_pet(client, auth_headers):
    pet_id = register(client, log_in(client, "bob@example.com")).json()["id"]

    assert client.get(f"/pets/{pet_id}", headers=auth_headers).status_code == 403


def test_pet_routes_require_token(client, auth_headers):
    pet_id = register(client, auth_headers).json()["id"]

    assert register(client, headers={}).status_code == 401
    assert client.get("/pets").status_code == 401
    assert client.get(f"/pets/{pet_id}").status_code == 401
