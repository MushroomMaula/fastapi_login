from typing import Callable, Iterator, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.db.models import User
from app.security import hash_password, manager


@manager.user_loader(session_provider=get_session)
def get_user_by_name(
    name: str,
    db: Optional[Session] = None,
    session_provider: Callable[[], Iterator[Session]] = None
) -> Optional[User]:
    """
    Queries the database for a user with the given name

    Args:
        name: The name of the user
        db: The currently active database sesssion
        session_provider: Optional method to retrieve a session if db is None (provided by our LoginManager)

    Returns:
        The user object or none
    """

    if db is None and session_provider is None:
        raise ValueError("db and session_provider cannot both be None.")

    if db is None:
        db = next(session_provider())

    user = db.query(User).where(User.username == name).first()
    return user


def create_user(name: str, password: str, db: Session, is_admin: bool = False) -> User:
    """
    Creates and commits a new user object to the database

    Args:
        name: The name of the user
        password: The plaintext password
        db: The active db session
        is_admin: Wether the user is a admin, defaults to false

    Returns:
        The newly created user.
    """
    hashed_pw = hash_password(password)
    user = User(username=name, password=hashed_pw, is_admin=is_admin)
    db.add(user)
    db.commit()
    return user
