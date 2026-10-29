from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.adapters.persistence.sqlalchemy.sqlalchemy_tables import metadata
from app.config import settings

config = context.config

# Logging settings from alembic.ini; keep the loggers the app already set up.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# The app's table definitions, compared with the database by `alembic check`.
target_metadata = metadata

# Tests pass the URL of their own database; everything else uses DATABASE_URL.
database_url = config.attributes.get("database_url", settings.database_url)


# `alembic upgrade head --sql`: print the SQL instead of running it.
def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# `alembic upgrade head`: connect and run the pending migrations in one transaction.
def run_migrations_online() -> None:
    engine = create_engine(database_url, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
