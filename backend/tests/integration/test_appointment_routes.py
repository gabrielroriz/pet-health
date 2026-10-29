from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain.appointment import PET_BUSY, VETERINARIAN_BUSY
from app.domain.hospital import Hospital
from app.domain.hospital_network import HospitalNetwork
from app.domain.veterinarian import Veterinarian
from tests.integration.conftest import add_hospital, add_veterinarian, log_in


def register_pet(client, headers, name: str = "Thor") -> str:
    return client.post("/pets", json={"name": name, "species": "dog"}, headers=headers).json()["id"]


@pytest.fixture
def hospital(session) -> Hospital:
    return add_hospital(session, network=HospitalNetwork(name="PetCare Network"))


@pytest.fixture
def veterinarian(session, hospital) -> Veterinarian:
    return add_veterinarian(session, hospital)


@pytest.fixture
def payload(client, auth_headers, hospital, veterinarian) -> dict:
    return {
        "pet_id": register_pet(client, auth_headers),
        "hospital_id": str(hospital.id),
        "veterinarian_id": str(veterinarian.id),
        "starts_at": "2030-01-01T10:00:00Z",
        "duration_minutes": 30,
        "reason": "Annual vaccines",
    }


def schedule(client, headers, payload, **overrides):
    return client.post("/appointments", json=payload | overrides, headers=headers)


def test_schedules_appointment_for_logged_in_user(client, auth_headers, payload):
    response = schedule(client, auth_headers, payload)

    assert response.status_code == 201
    body = response.json()
    assert body["owner_id"] == client.get("/auth/me", headers=auth_headers).json()["id"]
    assert body["pet_id"] == payload["pet_id"]
    assert body["hospital_id"] == payload["hospital_id"]
    assert body["veterinarian_id"] == payload["veterinarian_id"]
    assert datetime.fromisoformat(body["starts_at"]) == datetime(2030, 1, 1, 10, tzinfo=UTC)
    assert datetime.fromisoformat(body["ends_at"]) == datetime(2030, 1, 1, 10, 30, tzinfo=UTC)
    assert body["duration_minutes"] == 30
    assert body["reason"] == "Annual vaccines"
    assert body["status"] == "scheduled"


def test_lists_own_scheduled_appointments_earliest_first(client, auth_headers, payload):
    later = schedule(client, auth_headers, payload, starts_at="2030-01-01T15:00:00Z").json()
    earlier = schedule(client, auth_headers, payload, starts_at="2030-01-01T09:00:00Z").json()

    response = client.get("/appointments", headers=auth_headers)

    assert response.status_code == 200
    assert [a["id"] for a in response.json()] == [earlier["id"], later["id"]]
    assert client.get("/appointments", headers=log_in(client, "bob@example.com")).json() == []


def test_rejects_overlap_with_same_veterinarian(client, auth_headers, payload):
    schedule(client, auth_headers, payload)
    luna = register_pet(client, auth_headers, "Luna")

    response = schedule(client, auth_headers, payload, pet_id=luna, starts_at="2030-01-01T10:15:00Z")

    assert response.status_code == 409
    assert response.json() == {"detail": VETERINARIAN_BUSY}


def test_rejects_overlap_with_same_pet(client, auth_headers, payload, session, hospital):
    schedule(client, auth_headers, payload)
    another = add_veterinarian(session, hospital, name="Dr. Carlos Lima")

    response = schedule(client, auth_headers, payload, veterinarian_id=str(another.id))

    assert response.status_code == 409
    assert response.json() == {"detail": PET_BUSY}


def test_accepts_back_to_back_appointments(client, auth_headers, payload):
    schedule(client, auth_headers, payload)

    assert schedule(client, auth_headers, payload, starts_at="2030-01-01T10:30:00Z").status_code == 201
    assert schedule(client, auth_headers, payload, starts_at="2030-01-01T09:30:00Z").status_code == 201


def test_cancels_appointment_and_frees_its_time(client, auth_headers, payload):
    appointment_id = schedule(client, auth_headers, payload).json()["id"]

    response = client.post(f"/appointments/{appointment_id}/cancel", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    assert client.get("/appointments", headers=auth_headers).json() == []
    assert schedule(client, auth_headers, payload).status_code == 201


def test_rejects_cancelling_twice(client, auth_headers, payload):
    appointment_id = schedule(client, auth_headers, payload).json()["id"]
    client.post(f"/appointments/{appointment_id}/cancel", headers=auth_headers)

    response = client.post(f"/appointments/{appointment_id}/cancel", headers=auth_headers)

    assert response.status_code == 409


@pytest.mark.parametrize(
    "overrides",
    [
        {"starts_at": "2030-01-01T10:00:00"},
        {"starts_at": "not-a-date"},
        {"duration_minutes": 10},
        {"duration_minutes": 300},
        {"reason": ""},
        {"veterinarian_id": None},
        {"room": "3"},
    ],
)
def test_rejects_invalid_payload(client, auth_headers, payload, overrides):
    assert schedule(client, auth_headers, payload, **overrides).status_code == 422


def test_rejects_appointment_in_the_past(client, auth_headers, payload):
    yesterday = (datetime.now(UTC) - timedelta(days=1)).isoformat()

    response = schedule(client, auth_headers, payload, starts_at=yesterday)

    assert response.status_code == 422
    assert response.json() == {"detail": "Appointments must start in the future."}


def test_rejects_veterinarian_of_another_hospital(client, auth_headers, payload, session):
    elsewhere = add_hospital(session, name="Happy Paws Clinic")

    response = schedule(client, auth_headers, payload, hospital_id=str(elsewhere.id))

    assert response.status_code == 422
    assert response.json() == {"detail": "The veterinarian doesn't work at this hospital."}


@pytest.mark.parametrize("field", ["pet_id", "hospital_id", "veterinarian_id"])
def test_returns_404_for_unknown_reference(client, auth_headers, payload, field):
    assert schedule(client, auth_headers, payload, **{field: str(uuid4())}).status_code == 404


def test_returns_403_for_another_users_pet(client, auth_headers, payload):
    bobs_pet = register_pet(client, log_in(client, "bob@example.com"), "Rex")

    assert schedule(client, auth_headers, payload, pet_id=bobs_pet).status_code == 403


def test_returns_403_when_cancelling_another_users_appointment(client, auth_headers, payload):
    appointment_id = schedule(client, auth_headers, payload).json()["id"]
    bob = log_in(client, "bob@example.com")

    assert client.post(f"/appointments/{appointment_id}/cancel", headers=bob).status_code == 403


def test_returns_404_when_cancelling_unknown_appointment(client, auth_headers):
    assert client.post(f"/appointments/{uuid4()}/cancel", headers=auth_headers).status_code == 404


def test_appointment_routes_require_token(client, payload):
    assert client.get("/appointments").status_code == 401
    assert client.post("/appointments", json=payload).status_code == 401
    assert client.post(f"/appointments/{uuid4()}/cancel").status_code == 401
