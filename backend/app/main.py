from fastapi import FastAPI
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.http.error_handlers import register_error_handlers
from app.adapters.http.routers import (
    appointment_routes,
    auth_routes,
    hospital_routes,
    pet_routes,
    veterinarian_routes,
)
from app.adapters.persistence.sqlalchemy.sqlalchemy_session import create_session_factory
from app.adapters.security.in_memory.in_memory_token_service import InMemoryTokenService
from app.config import settings


def create_app(session_factory: sessionmaker[Session] | None = None) -> FastAPI:
    app = FastAPI(title=settings.app_name)
    # Every request opens a database session from this factory; tests pass one for their own database.
    app.state.session_factory = session_factory or create_session_factory(settings.database_url)
    # Login tokens live in memory, so restarting the server logs everyone out.
    app.state.tokens = InMemoryTokenService()

    # Domain errors raised anywhere become HTTP responses (401, 403, 404, 409, 422).
    register_error_handlers(app)
    # Plug in each group of endpoints: /auth, /pets, /hospitals, /veterinarians, /appointments.
    app.include_router(auth_routes.router)
    app.include_router(pet_routes.router)
    app.include_router(hospital_routes.router)
    app.include_router(veterinarian_routes.router)
    app.include_router(appointment_routes.router)

    @app.get("/")
    def read_root():
        return {"message": "Hello, World!"}

    return app


# The app that uvicorn and `fastapi dev` serve.
app = create_app()
