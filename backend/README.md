# Backend

The API stores its data in PostgreSQL. From the repository root, start the database:

```bash
docker compose up -d db
```

Then, from `backend/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
python -m app.seed   # optional: hospitals, veterinarians, and ana@example.com with two pets
fastapi dev
```

The API runs at http://localhost:8000 and the docs at http://localhost:8000/docs.

Settings are read from environment variables or a `.env` file (see `app/config.py`). `DATABASE_URL` defaults to `postgresql+psycopg://pet_health:pet_health@localhost:5432/pet_health`. If port 5432 is taken, start the database on another one and point `DATABASE_URL` at it:

```bash
DB_PORT=5435 docker compose up -d db
echo 'DATABASE_URL=postgresql+psycopg://pet_health:pet_health@localhost:5435/pet_health' > .env
```

## Migrations

The schema lives in `migrations/`. After changing `app/adapters/persistence/sqlalchemy/sqlalchemy_tables.py`:

```bash
alembic revision -m "describe the change"   # then write upgrade() and downgrade()
alembic upgrade head
alembic check                               # fails if tables, columns, indexes or foreign keys differ
```

## Docker

From the repository root:

```bash
docker compose up --build
```

This starts PostgreSQL, runs the migrations, seeds the development data, and serves the API with Uvicorn at http://localhost:8000. Uvicorn reloads when files in `app/` change. Set `BACKEND_PORT` or `DB_PORT` to use other host ports (`BACKEND_PORT=8001 DB_PORT=5435 docker compose up`). Rebuild after changing `requirements.txt`.

## Tests

```bash
pytest
```

Integration tests need the database running. They create a `<database>_test` database on the same server, migrate it, and empty it before each test, so they never touch your development data. Unit tests don't need a database: `pytest tests/unit`.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the internal structure.
