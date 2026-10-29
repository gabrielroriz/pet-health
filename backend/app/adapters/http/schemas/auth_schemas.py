from typing import Self
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.domain.user import User


# Development login: just an email, no password.
class LoginRequest(BaseModel):
    email: EmailStr


# The token to send back as 'Authorization: Bearer <token>'.
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str

    @classmethod
    def from_domain(cls, user: User) -> Self:
        return cls(id=user.id, email=user.email)
