from app.application.ports.services.token_service import TokenService
from app.application.ports.repositories.user_repository import UserRepository
from app.domain.user import User


class LogIn:
    """Passwordless login for local development: any email gets a token."""

    def __init__(self, users: UserRepository, tokens: TokenService) -> None:
        self.users = users
        self.tokens = tokens

    def execute(self, email: str) -> str:
        # Building the User normalizes the email and rejects a blank one (422).
        user = User(email=email)
        # The first login creates the user; later logins reuse it.
        existing = self.users.get_by_email(user.email)
        if existing is None:
            self.users.add(user)
        else:
            user = existing
        # Each login gets a fresh token.
        return self.tokens.issue(user.id)
