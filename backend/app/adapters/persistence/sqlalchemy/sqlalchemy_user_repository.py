from uuid import UUID

from sqlalchemy import Row, insert, select
from sqlalchemy.orm import Session

from app.adapters.persistence.sqlalchemy.sqlalchemy_tables import users
from app.domain.user import User


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, user: User) -> None:
        # Insert and commit at once: each repository write is its own transaction.
        self.session.execute(insert(users).values(id=user.id, email=user.email))
        self.session.commit()

    def get(self, user_id: UUID) -> User | None:
        # Look up by id and map the row to a domain User.
        row = self.session.execute(select(users).where(users.c.id == user_id)).one_or_none()
        return _to_user(row) if row else None

    def get_by_email(self, email: str) -> User | None:
        # Look up by email, already normalized by User.
        row = self.session.execute(select(users).where(users.c.email == email)).one_or_none()
        return _to_user(row) if row else None


def _to_user(row: Row) -> User:
    return User(id=row.id, email=row.email)
