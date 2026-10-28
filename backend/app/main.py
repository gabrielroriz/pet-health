from fastapi import FastAPI

from app.adapters.http.error_handlers import register_error_handlers
from app.adapters.http.routers import auth_routes, pet_routes
from app.adapters.persistence.in_memory.in_memory_pet_repository import InMemoryPetRepository
from app.adapters.persistence.in_memory.in_memory_user_repository import InMemoryUserRepository
from app.adapters.security.in_memory.in_memory_token_service import InMemoryTokenService
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.state.pets = InMemoryPetRepository()
    app.state.users = InMemoryUserRepository()
    app.state.tokens = InMemoryTokenService()

    register_error_handlers(app)
    app.include_router(auth_routes.router)
    app.include_router(pet_routes.router)

    @app.get("/")
    def read_root():
        return {"message": "Hello, World!"}

    return app


app = create_app()
