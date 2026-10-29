from dataclasses import dataclass, field
from uuid import UUID, uuid4

from app.domain.errors import InvalidUserData


@dataclass
class User:
    email: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        # Normalize so the same email always maps to the same user.
        self.email = self.email.strip().lower()
        if not self.email:
            raise InvalidUserData("Email must not be blank.")
