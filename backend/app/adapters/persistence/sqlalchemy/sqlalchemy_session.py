from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_factory(database_url: str) -> sessionmaker[Session]:
    # One connection pool per app; pre_ping replaces connections the database dropped.
    return sessionmaker(create_engine(database_url, pool_pre_ping=True))
