from app.application.ports.services.token_service import TokenService
from app.application.ports.repositories.user_repository import UserRepository
from app.domain.errors import NotAuthenticated
from app.domain.user import User


class Authenticate:
    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self.users = users
        self.tokens = tokens

    def execute(self, token: str) -> User:
        # Find which user the token was issued to.
        user_id = self.tokens.verify(token)
        # Load that user from the database.
        user = self.users.get(user_id) if user_id is not None else None
        # Unknown token or missing user: 401.
        if user is None:
            raise NotAuthenticated("Invalid or expired token.")
        return user
