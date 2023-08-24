from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret: str = ""  # automatically taken from environment variable
    database_uri: str = "sqlite:///app.db"
    token_url: str = "/auth/token"


DEFAULT_SETTINGS = Settings(_env_file=".env")
