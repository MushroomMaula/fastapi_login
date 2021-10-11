from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.security import hash_password


def get_user_by_name(name: str, db: Session) -> Optional[User]:
    """
    Queries the database for a user with the given name

    Args:
        name: The name of the user
        db: The currently active database sesssion

    Returns:
        The user object or none
    """
    query = select(User).where(User.username == name)
    result = db.execute(query)
    return result.fetchone()


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
