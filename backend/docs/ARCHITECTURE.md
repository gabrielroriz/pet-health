# Backend architecture

The backend follows a simple **hexagonal architecture** (ports and adapters). Business rules sit at the center and know nothing about HTTP, databases or token formats. Those details live in adapters at the edge and can be swapped without touching the core.

## Layers

```
┌───────────────────────────────────────────────┐
│ adapters   (FastAPI, persistence, security)   │
│   ┌───────────────────────────────────────┐   │
│   │ application   (use cases, ports)      │   │
│   │   ┌───────────────────────────────┐   │   │
│   │   │ domain   (entities, rules)    │   │   │
│   │   └───────────────────────────────┘   │   │
│   └───────────────────────────────────────┘   │
└───────────────────────────────────────────────┘
```

### Dependency rule

Imports only point inward:

- `domain` imports nothing from the other layers.
- `application` imports from `domain`.
- `adapters` import from `application` and `domain`.
- `main.py` is the only place that knows every layer, because it wires adapters to ports.

Never import FastAPI, SQLAlchemy, JWT libraries or `app.adapters` from `domain` or `application`.

## Directory layout

```
backend/
├── alembic.ini                  # Alembic settings. The database URL comes from DATABASE_URL
├── migrations/                  # Alembic migrations: tables and the constraints that guard the data
├── app/
│   ├── main.py                  # Composition root: builds the app, registers routers and error handlers
│   ├── config.py                # Settings read from environment variables or .env
│   ├── seed.py                  # Development data: a hospital network, hospitals, veterinarians, a user and pets
│   ├── domain/                  # Entities, value objects, business rules, domain errors
│   ├── application/
│   │   ├── ports/               # Protocols the use cases depend on: repositories/ and services/, one file per port
│   │   └── use_cases/           # One class per use case, with an execute() method, grouped by domain (pets/, appointments/, ...)
│   └── adapters/
│       ├── http/                # Inbound adapter: FastAPI
│       │   ├── routers/         # Endpoints: parse the request, call a use case, map the response
│       │   ├── schemas/         # Pydantic request and response models, one file per domain
│       │   ├── dependencies/    # Depends() factories that build use cases, plus get_current_user. persistence_dependencies.py opens the request's session and builds the repositories
│       │   └── error_handlers.py # Turns domain errors into HTTP responses
│       ├── persistence/         # Outbound adapters that implement the repository ports: sqlalchemy/ (PostgreSQL) and in_memory/ (unit tests)
│       └── security/            # Outbound adapters for tokens and password hashing, one folder per technology
└── tests/
    ├── unit/                    # Domain and use cases, tested with in-memory adapters
    └── integration/             # HTTP routes and SQLAlchemy repositories, against PostgreSQL
```

## Where each concern lives

| Concern | Location | What it covers |
|---|---|---|
| Payload validation | `adapters/http/schemas/` | The shape and format of a request: types, required fields, lengths, formats. |
| Business validation | `domain/` | Rules that hold however a request arrives, such as "a pet's birth date can't be in the future". |
| Authentication | `adapters/http/dependencies/auth_dependencies.py` | Reads the bearer token and resolves the current user through the `Authenticate` use case. See [Authentication](#authentication). |
| Authorization | `application/use_cases/` | Decides whether the current user may act on a resource, and raises `NotAllowed` if not. |
| Error mapping | `adapters/http/error_handlers.py` | Turns domain errors into status codes such as 404, 403 and 422. The domain never raises `HTTPException`. |
| Persistence | `adapters/persistence/` | Implements the repository protocols: `sqlalchemy/` for PostgreSQL, which the app uses, and `in_memory/` for unit tests. Use cases see only the protocols. |
| Transactions | `adapters/persistence/sqlalchemy/` | Each request gets one session. Every repository write commits on its own, so a use case saves with a single write. |
| Data integrity | `migrations/` | Keys, checks and exclusion constraints that hold even if a bug or a script skips the domain rules. `sqlalchemy_tables.py` mirrors the schema for queries and `alembic check`. |
| Configuration | `config.py` | Settings from environment variables or `.env`, read once into `settings`. |
| Wiring | `main.py`, `adapters/http/dependencies/` | FastAPI's `Depends` builds use cases from concrete adapters. No DI framework is used. |

## A request end to end

1. A router in `adapters/http/routers/` receives the request. FastAPI validates the body against a Pydantic schema and returns 422 if it's malformed.
2. The `get_current_user` dependency authenticates the caller.
3. A dependency factory builds the use case with its concrete adapters.
4. The use case runs the business logic: it checks authorization, applies domain rules and talks to repositories through ports.
5. The router converts the result into a response schema. If a domain error was raised instead, `error_handlers.py` turns it into an HTTP response.

```python
@router.post("", response_model=PetResponse, status_code=status.HTTP_201_CREATED)
def register_pet(
    payload: RegisterPetRequest,                                  # payload validation
    user: Annotated[User, Depends(get_current_user)],             # authentication
    use_case: Annotated[RegisterPet, Depends(get_register_pet)],  # wiring
) -> PetResponse:
    pet = use_case.execute(owner_id=user.id, **payload.model_dump())  # business rules
    return PetResponse.from_domain(pet)
```

Routers are the only code that knows about HTTP. Use cases can be tested without FastAPI or a database.

## Adding a feature

1. Model the concept and its rules in `domain/`, with any new errors in `domain/errors.py`.
2. Declare what the use case needs from outside as a protocol in `application/ports/`: repositories go in `ports/repositories/<entity>_repository.py`.
3. Write the use case in `application/use_cases/<domain>/` and unit-test it with an in-memory adapter.
4. Implement the port in `adapters/persistence/<technology>/<technology>_<entity>_repository.py` (or another outbound adapter). For new tables, update `sqlalchemy_tables.py`, add a migration with `alembic revision -m "..."`, and confirm with `alembic check`.
5. Add the request and response schemas, the router and the dependency factory in `adapters/http/` (`<entity>_schemas.py`, `<entity>_routes.py`, `<entity>_dependencies.py`), and register the router in `main.py`.
6. Map any new domain errors in `adapters/http/error_handlers.py`.
7. Add integration tests and example requests to `api.http`.

## Authentication

The auth method hasn't been chosen yet, so the API ships with a **development login** that makes it easy to try the API locally:

1. `POST /auth/login` with `{"email": "..."}` returns a token. There's no password, and an unknown email creates a new user.
2. Protected routes expect the header `Authorization: Bearer <token>`. In the docs at `/docs`, use the **Authorize** button.
3. `GET /auth/me` returns the logged-in user.

Users are stored in PostgreSQL, but tokens are random strings kept in memory by `InMemoryTokenService`, so restarting the server logs everyone out. **This login is not safe for production.**

How it fits the layers:

| Piece | Location |
|---|---|
| `UserRepository` and `TokenService` ports | `application/ports/repositories/user_repository.py`, `application/ports/services/token_service.py` |
| `LogIn` (find or create the user, issue a token) and `Authenticate` (token to user) use cases | `application/use_cases/auth/` |
| User repository and in-memory token service | `adapters/persistence/sqlalchemy/sqlalchemy_user_repository.py`, `adapters/security/in_memory/in_memory_token_service.py` |
| Bearer header parsing and `get_current_user` | `adapters/http/dependencies/auth_dependencies.py` |
| Login and "me" routes | `adapters/http/routers/auth_routes.py` |

To switch to a real auth method, replace the token service adapter, for example with one that verifies JWTs from your own login or from a provider such as Auth0 or Supabase. Then replace or remove `LogIn` and the login route. Routes and use cases that depend on `get_current_user` don't change.

## Appointments

A user books an appointment for one of their pets with a veterinarian at a hospital. A hospital belongs to at most one network, and a veterinarian can work at several hospitals.

```
hospital_networks 1 ── 0..n hospitals n ── n veterinarians      (hospital_veterinarians)
users 1 ── n pets 1 ── n appointments n ── 1 (hospital, veterinarian)
users 1 ──────────────── n appointments                          (owner_id: who booked it)
```

| Endpoint | What it does |
|---|---|
| `GET /pets` | The user's pets, to pick one |
| `GET /hospitals` | Hospitals with their network |
| `GET /veterinarians` | Veterinarians with the hospitals they work at |
| `GET /veterinarians/available?hospital_id=&starts_at=&duration_minutes=` | Veterinarians of the hospital with no appointment, at any hospital, during that time |
| `GET /appointments` | The user's scheduled appointments, earliest first |
| `POST /appointments` | Books an appointment. 409 if the veterinarian or the pet is busy at that time |
| `POST /appointments/{id}/cancel` | Cancels it. The row stays with status `cancelled` and its time is free again |

Rules: appointments start in the future and last 15 to 240 minutes. The veterinarian must work at the chosen hospital. Neither the veterinarian nor the pet can have two scheduled appointments that overlap, at any hospital. One appointment may start exactly when another ends.

### Double-booking protection

Three layers guard against overlaps. Each one catches what the previous one can't:

1. **Domain check.** `ScheduleAppointment` loads the scheduled appointments that overlap the new one and calls `Appointment.ensure_no_conflict_with`. This gives clear errors for the usual case, where requests don't race.
2. **Optimistic lock.** Every veterinarian has an `agenda_version`. The use case reads it *before* the check, and `AppointmentRepository.add` saves only if it is unchanged: `UPDATE veterinarians SET agenda_version = n + 1 WHERE id = ? AND agenda_version = n`, in the same transaction as the insert. If two requests for the same veterinarian race, the first to commit wins. The other matches no row and gets `AgendaChanged`, then retries from a fresh read, up to 3 attempts. If it overlaps the winner, the retry fails with `DoubleBooking`; any other time goes through. Any rule checked in the domain is protected this way, including ones the database can't express.
3. **Database constraints.** Two exclusion constraints, `EXCLUDE USING gist (veterinarian_id WITH =, tstzrange(starts_at, ends_at) WITH &&) WHERE (status = 'scheduled')` and the same for `pet_id`, make overlaps impossible whatever the code does. They need the `btree_gist` extension. The repository turns their violations into `DoubleBooking`. This layer catches overlaps for the same pet with two different veterinarians, which the veterinarian's lock doesn't cover.

A composite foreign key from `appointments (hospital_id, veterinarian_id)` to `hospital_veterinarians` also ensures that the veterinarian works at the hospital.

`InMemoryAppointmentRepository` applies the same version check and no-overlap rule, so unit tests can simulate races. `tests/integration/adapters/persistence/sqlalchemy/test_sqlalchemy_appointment_repository.py` runs real concurrent bookings against PostgreSQL.

## Current status

The structure is being built in steps:

| Step | Scope | Status |
|---|---|---|
| 1 | `app/` package, settings, pytest setup | Done |
| 2 | Domain layer: `Pet`, `User`, domain errors | Done |
| 3 | Application layer: repository port, `RegisterPet` and `GetPet` use cases | Done |
| 4 | In-memory persistence adapter | Done |
| 5 | HTTP adapter: schemas, routers, error mapping | Done |
| 6 | Authentication: in-memory development login | Done |
| 7 | Backend CI: lint, tests, import rules | To do |
| 8 | SQLAlchemy persistence adapter, PostgreSQL and Alembic migrations | Done |
| 9 | Appointments, hospitals, networks and veterinarians | Done |

Directories listed in the layout above appear as their step is implemented.
