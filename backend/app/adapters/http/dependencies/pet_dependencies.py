from app.adapters.http.dependencies.persistence_dependencies import PetRepositoryDep
from app.application.use_cases.pets.get_pet import GetPet
from app.application.use_cases.pets.list_pets import ListPets
from app.application.use_cases.pets.register_pet import RegisterPet


# FastAPI calls these per request to build each use case with its repositories.
def get_register_pet(pets: PetRepositoryDep) -> RegisterPet:
    return RegisterPet(pets)


def get_get_pet(pets: PetRepositoryDep) -> GetPet:
    return GetPet(pets)


def get_list_pets(pets: PetRepositoryDep) -> ListPets:
    return ListPets(pets)
