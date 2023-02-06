import pathlib
import os

from dotenv import load_dotenv
from pydantic import BaseSettings

root = pathlib.Path(__file__).parent.parent
# This will always give the correct path as long as .env is in the parent directory
env_file = root / '.env'
load_dotenv(env_file)

class Settings(BaseSettings):

    project_root: pathlib.Path = root
    secret: str = os.getenv('SECRET', 'elf-of-era')
    db_uri: str = "sqlite+pysqlite:///app.db"
    token_url: str = "/auth/login"


Config = Settings(_env_file=env_file)
