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
├── app/
│   ├── main.py                  # Composition root: builds the app, registers routers and error handlers
│   ├── config.py                # Settings read from environment variables or .env
│   ├── domain/                  # Entities, value objects, business rules, domain errors
│   ├── application/
│   │   ├── ports.py             # Protocols the use cases depend on (repositories, token service, ...)
│   │   └── use_cases/           # One class per use case, with an execute() method
│   └── adapters/
│       ├── http/                # Inbound adapter: FastAPI
│       │   ├── routers/         # Endpoints: parse the request, call a use case, map the response
│       │   ├── schemas.py       # Pydantic request and response models
│       │   ├── auth.py          # get_current_user dependency
│       │   ├── dependencies.py  # Depends() factories that build use cases
│       │   └── errors.py        # Turns domain errors into HTTP responses
│       ├── persistence/         # Outbound adapters that implement the repository ports
│       └── security/            # Outbound adapters for tokens and password hashing
└── tests/
    ├── unit/                    # Domain and use cases, tested with in-memory adapters
    └── integration/             # HTTP tests through FastAPI's TestClient
```

## Where each concern lives

| Concern | Location | What it covers |
|---|---|---|
| Payload validation | `adapters/http/schemas.py` | The shape and format of a request: types, required fields, lengths, formats. |
| Business validation | `domain/` | Rules that hold however a request arrives, such as "a pet's birth date can't be in the future". |
| Authentication | `adapters/http/auth.py` | Reads the token through the `TokenService` port and returns the current user. |
| Authorization | `application/use_cases/` | Decides whether the current user may act on a resource, and raises `NotAllowed` if not. |
| Error mapping | `adapters/http/errors.py` | Turns domain errors into status codes such as 404, 403 and 422. The domain never raises `HTTPException`. |
| Persistence | `adapters/persistence/` | Implements the repository protocols. Use cases see only the protocols. |
| Configuration | `config.py` | Settings from environment variables or `.env`, read once into `settings`. |
| Wiring | `main.py`, `adapters/http/dependencies.py` | FastAPI's `Depends` builds use cases from concrete adapters. No DI framework is used. |

## A request end to end

1. A router in `adapters/http/routers/` receives the request. FastAPI validates the body against a Pydantic schema and returns 422 if it's malformed.
2. The `get_current_user` dependency authenticates the caller.
3. A dependency factory builds the use case with its concrete adapters.
4. The use case runs the business logic: it checks authorization, applies domain rules and talks to repositories through ports.
5. The router converts the result into a response schema. If a domain error was raised instead, `errors.py` turns it into an HTTP response.

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
2. Declare what the use case needs from outside as a protocol in `application/ports.py`.
3. Write the use case in `application/use_cases/` and unit-test it with an in-memory adapter.
4. Implement the port in `adapters/persistence/` (or another outbound adapter).
5. Add the request and response schemas, the router and the dependency factory in `adapters/http/`, and register the router in `main.py`.
6. Map any new domain errors in `adapters/http/errors.py`.
7. Add integration tests and example requests to `api.http`.

## Current status

The structure is being built in steps:

| Step | Scope | Status |
|---|---|---|
| 1 | `app/` package, settings, pytest setup | Done |
| 2 | Domain layer: `Pet`, `User`, domain errors | Done |
| 3 | Application layer: repository port, `RegisterPet` and `GetPet` use cases | Done |
| 4 | In-memory persistence adapter | Done |
| 5 | HTTP adapter: schemas, routers, error mapping | Done |
| 6 | Authentication | To do |
| 7 | Backend CI: lint, tests, import rules | To do |
| 8 | SQLAlchemy persistence adapter | Later |

Directories listed in the layout above appear as their step is implemented.
