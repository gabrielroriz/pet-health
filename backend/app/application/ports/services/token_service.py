from typing import Protocol
from uuid import UUID


# Issues login tokens and maps them back to the user they belong to.
class TokenService(Protocol):
    def issue(self, user_id: UUID) -> str: ...

    def verify(self, token: str) -> UUID | None: ...
