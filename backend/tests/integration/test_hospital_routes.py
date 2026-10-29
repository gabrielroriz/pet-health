from app.domain.hospital_network import HospitalNetwork
from tests.integration.conftest import add_hospital


def test_lists_hospitals_with_their_network(client, auth_headers, session):
    network = HospitalNetwork(name="PetCare Network")
    downtown = add_hospital(session, "PetCare Downtown", network)
    happy_paws = add_hospital(session, "Happy Paws Clinic")

    response = client.get("/hospitals", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == [
        {"id": str(happy_paws.id), "name": "Happy Paws Clinic", "network": None},
        {
            "id": str(downtown.id),
            "name": "PetCare Downtown",
            "network": {"id": str(network.id), "name": "PetCare Network"},
        },
    ]


def test_hospital_routes_require_token(client):
    assert client.get("/hospitals").status_code == 401
