from fastapi import FastAPI

from app.adapters.http.errors import register_error_handlers
from app.adapters.http.routers import auth, pets
from app.adapters.persistence.in_memory import (
    InMemoryPetRepository,
    InMemoryUserRepository,
)
from app.adapters.security.in_memory_tokens import InMemoryTokenService
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.state.pets = InMemoryPetRepository()
    app.state.users = InMemoryUserRepository()
    app.state.tokens = InMemoryTokenService()

    register_error_handlers(app)
    app.include_router(auth.router)
    app.include_router(pets.router)

    @app.get("/")
    def read_root():
        return {"message": "Hello, World!"}

    return app


app = create_app()
