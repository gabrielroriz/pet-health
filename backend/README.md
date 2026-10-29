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
python -m app.seed   # optional: hospitals, veterinarians, and ana@example.com and bob@example.com with pets
fastapi dev
```

The API runs at http://localhost:8000 and the docs at http://localhost:8000/docs.

Settings are read from environment variables or a `.env` file (see `app/config.py`). `DATABASE_URL` defaults to `postgresql+psycopg://pet_health:pet_health@localhost:5432/pet_health`. If port 5432 is taken, start the database on another one and point `DATABASE_URL` at it:

```bash
DB_PORT=5435 docker compose up -d db
echo 'DATABASE_URL=postgresql+psycopg://pet_health:pet_health@localhost:5435/pet_health' > .env
```

## Data model

```mermaid
erDiagram
    users ||--o{ pets : owns
    users ||--o{ appointments : books
    pets ||--o{ appointments : "is seen in"
    hospital_networks |o--o{ hospitals : groups
    hospitals ||--o{ hospital_veterinarians : employs
    veterinarians ||--o{ hospital_veterinarians : "works at"
    hospital_veterinarians ||--o{ appointments : "takes place with"

    users {
        uuid id PK
        varchar email UK
    }
    pets {
        uuid id PK
        uuid owner_id FK
        varchar name
        varchar species "dog, cat, bird, rabbit or other"
        date birth_date "nullable"
        varchar breed "nullable"
    }
    hospital_networks {
        uuid id PK
        varchar name UK
    }
    hospitals {
        uuid id PK
        varchar name
        uuid network_id FK "nullable"
    }
    veterinarians {
        uuid id PK
        varchar name
        int agenda_version "optimistic lock"
    }
    hospital_veterinarians {
        uuid hospital_id PK, FK
        uuid veterinarian_id PK, FK
    }
    appointments {
        uuid id PK
        uuid owner_id FK "the user who booked it"
        uuid pet_id FK
        uuid hospital_id FK "with veterinarian_id"
        uuid veterinarian_id FK "with hospital_id"
        timestamptz starts_at
        timestamptz ends_at
        varchar reason
        varchar status "scheduled or cancelled"
    }
```

- A hospital belongs to at most one network, and a veterinarian can work at several hospitals through `hospital_veterinarians`.
- `(hospital_id, veterinarian_id)` in `appointments` is one foreign key to `hospital_veterinarians`, so an appointment's veterinarian always works at its hospital.
- No two scheduled appointments may overlap for the same veterinarian or the same pet, at any hospital. Two exclusion constraints enforce it, and cancelled appointments don't count. One appointment may start exactly when another ends.
- Every booking bumps the veterinarian's `agenda_version`, which works as an optimistic lock against concurrent bookings. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#double-booking-protection).
- Check constraints: `species` and `status` take only the listed values, and `ends_at` comes after `starts_at`.

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

This starts PostgreSQL, runs the migrations, seeds the development data, serves the API with Uvicorn at http://localhost:8000, and serves the frontend with the Vite dev server at http://localhost:5173. Uvicorn reloads when files in `app/` change, and Vite when files in `frontend/src/` change. Set `BACKEND_PORT`, `DB_PORT` or `FRONTEND_PORT` to use other host ports (`BACKEND_PORT=8001 DB_PORT=5435 FRONTEND_PORT=5174 docker compose up`). Rebuild after changing `requirements.txt` or `frontend/package.json`.

## Tests

```bash
pytest
```

Integration tests need the database running. They create a `<database>_test` database on the same server, migrate it, and empty it before each test, so they never touch your development data. Unit tests don't need a database: `pytest tests/unit`.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the internal structure.
