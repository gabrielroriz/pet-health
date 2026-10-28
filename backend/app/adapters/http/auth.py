from uuid import UUID

from app.domain.user import User

# Placeholder until authentication is added: every request acts as this user.
PLACEHOLDER_USER = User(
    email="placeholder@pet-health.local",
    id=UUID("00000000-0000-0000-0000-000000000001"),
)


def get_current_user() -> User:
    return PLACEHOLDER_USER
