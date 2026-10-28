from app.application.ports import TokenService, UserRepository
from app.domain.user import User


class LogIn:
    """Passwordless login for local development: any email gets a token."""

    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self.users = users
        self.tokens = tokens

    def execute(self, email: str) -> str:
        user = User(email=email)
        existing = self.users.get_by_email(user.email)
        if existing is None:
            self.users.add(user)
        else:
            user = existing
        return self.tokens.issue(user.id)
