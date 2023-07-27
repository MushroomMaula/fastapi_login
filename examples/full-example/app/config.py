import pathlib

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

root = pathlib.Path(__file__).parent.parent
# This will always give the correct path as long as .env is in the parent directory
env_file = root / '.env'


class Settings(BaseSettings):
    project_root: pathlib.Path = root
    secret: str = ""
    db_uri: str = "sqlite+pysqlite:///app.db"
    token_url: str = "/auth/login"
    model_config = ConfigDict(env_file='.env')


Config = Settings(_env_file=env_file)
