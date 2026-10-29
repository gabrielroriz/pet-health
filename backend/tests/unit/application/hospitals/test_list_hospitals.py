from app.adapters.persistence.in_memory.in_memory_hospital_repository import (
    InMemoryHospitalRepository,
)
from app.application.use_cases.hospitals.list_hospitals import ListHospitals
from app.domain.hospital import Hospital
from app.domain.hospital_network import HospitalNetwork


def test_lists_hospitals_by_name_with_their_network():
    hospitals = InMemoryHospitalRepository()
    network = HospitalNetwork(name="PetCare Network")
    riverside = Hospital(name="PetCare Riverside", network=network)
    happy_paws = Hospital(name="Happy Paws Clinic")
    hospitals.add(riverside)
    hospitals.add(happy_paws)

    listed = ListHospitals(hospitals).execute()

    assert listed == [happy_paws, riverside]
    assert listed[1].network is network
