from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Session

from app.config import Config


Base = declarative_base()
engine = create_engine(Config.db_uri, future=True, connect_args={"check_same_thread": False})


def create_tables(_args=None):
    """
    Creates the tables specified in app.db.models

    Args:
        _args: Arguments parsed from the command line when used from the cli
    """
    # Needed for the models to be discovered
    from app.db.models import User, Post  # noqa F401
    print(f"Creating database at: {engine.url}")
    Base.metadata.create_all(engine)


def get_session():
    with Session(engine) as sess:
        yield sess
