from uuid import uuid4

import pytest

from app.domain.hospital import Hospital
from tests.integration.conftest import add_hospital, add_veterinarian


@pytest.fixture
def downtown(session) -> Hospital:
    return add_hospital(session, "PetCare Downtown")


@pytest.fixture
def riverside(session) -> Hospital:
    return add_hospital(session, "PetCare Riverside")


def available(client, headers, hospital_id, starts_at="2030-01-01T10:00:00Z", duration_minutes=30):
    params = {"hospital_id": str(hospital_id), "starts_at": starts_at, "duration_minutes": duration_minutes}
    return client.get("/veterinarians/available", params=params, headers=headers)


def test_lists_veterinarians_with_their_hospitals(client, auth_headers, session, downtown, riverside):
    beatriz = add_veterinarian(session, downtown, riverside, name="Dr. Beatriz Costa")

    response = client.get("/veterinarians", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": str(beatriz.id),
            "name": "Dr. Beatriz Costa",
            "hospital_ids": sorted(str(h) for h in beatriz.hospital_ids),
        }
    ]


def test_lists_veterinarians_available_at_hospital_and_time(
    client, auth_headers, session, downtown, riverside
):
    beatriz = add_veterinarian(session, downtown, riverside, name="Dr. Beatriz Costa")
    add_veterinarian(session, downtown, name="Dr. Carlos Lima")
    add_veterinarian(session, riverside, name="Dr. Daniela Rocha")
    pet_id = client.post("/pets", json={"name": "Thor", "species": "dog"}, headers=auth_headers).json()["id"]
    client.post(
        "/appointments",
        json={
            "pet_id": pet_id,
            "hospital_id": str(riverside.id),
            "veterinarian_id": str(beatriz.id),
            "starts_at": "2030-01-01T10:00:00Z",
            "duration_minutes": 30,
            "reason": "Check-up",
        },
        headers=auth_headers,
    )

    def names(starts_at):
        return [v["name"] for v in available(client, auth_headers, downtown.id, starts_at).json()]

    assert names("2030-01-01T10:15:00Z") == ["Dr. Carlos Lima"]
    assert names("2030-01-01T10:30:00Z") == ["Dr. Beatriz Costa", "Dr. Carlos Lima"]


def test_returns_404_for_unknown_hospital(client, auth_headers):
    assert available(client, auth_headers, uuid4()).status_code == 404


@pytest.mark.parametrize(
    "overrides",
    [
        {"starts_at": "2030-01-01T10:00:00"},
        {"duration_minutes": 0},
        {"hospital_id": "not-a-uuid"},
    ],
)
def test_rejects_invalid_query(client, auth_headers, downtown, overrides):
    params = {"hospital_id": str(downtown.id), "starts_at": "2030-01-01T10:00:00Z", "duration_minutes": 30}

    response = client.get("/veterinarians/available", params=params | overrides, headers=auth_headers)

    assert response.status_code == 422


def test_veterinarian_routes_require_token(client, downtown):
    assert client.get("/veterinarians").status_code == 401
    assert available(client, {}, downtown.id).status_code == 401
