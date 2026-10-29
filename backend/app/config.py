from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Pet Health API"
    # PostgreSQL connection; set DATABASE_URL in the environment or in .env to change it.
    database_url: str = "postgresql+psycopg://pet_health:pet_health@localhost:5435/pet_health"


# Read once at startup and imported wherever a setting is needed.
settings = Settings()
