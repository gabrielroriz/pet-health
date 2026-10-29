from app.application.ports.repositories.veterinarian_repository import VeterinarianRepository
from app.domain.veterinarian import Veterinarian


class ListVeterinarians:
    def __init__(self, veterinarians: VeterinarianRepository) -> None:
        self.veterinarians = veterinarians

    def execute(self) -> list[Veterinarian]:
        # Every veterinarian with the hospitals they work at, sorted by name.
        return self.veterinarians.list_all()
