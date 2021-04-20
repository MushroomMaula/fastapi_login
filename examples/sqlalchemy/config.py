from pydantic import BaseSettings


class Settings(BaseSettings):
    secret: str  # autmatically taken from environement variable
    database_uri: str = "sqlite:///app.db"
    token_url: str = "/auth/token"


DEFAULT_SETTINGS = Settings(_env_file=".env")
