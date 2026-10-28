from app.application.ports import TokenService, UserRepository
from app.domain.errors import NotAuthenticated
from app.domain.user import User


class Authenticate:
    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self.users = users
        self.tokens = tokens

    def execute(self, token: str) -> User:
        user_id = self.tokens.verify(token)
        user = self.users.get(user_id) if user_id is not None else None
        if user is None:
            raise NotAuthenticated("Invalid or expired token.")
        return user
