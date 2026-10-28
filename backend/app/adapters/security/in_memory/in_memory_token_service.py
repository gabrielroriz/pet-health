import secrets
from uuid import UUID


class InMemoryTokenService:
    """Random opaque tokens kept in memory. Restarting the server logs everyone out."""

    def __init__(self) -> None:
        self._tokens: dict[str, UUID] = {}

    def issue(self, user_id: UUID) -> str:
        token = secrets.token_urlsafe(32)
        self._tokens[token] = user_id
        return token

    def verify(self, token: str) -> UUID | None:
        return self._tokens.get(token)
