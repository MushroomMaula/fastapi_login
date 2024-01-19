from typing import Optional

from app.db import SessionLocal
from app.db.models import Post, User
from app.security import hash_password, manager
from sqlalchemy.orm import Session


def get_user_by_name(name: str, db: Session) -> Optional[User]:
    """
    Queries the database for a user with the given name

    Args:
        name: The name of the user
        db: The currently active database session

    Returns:
        The user object or none
    """
    user = db.query(User).where(User.username == name).first()
    return user


@manager.user_loader()
def get_user(name: str):
    with SessionLocal() as db:
        return get_user_by_name(name, db)


def create_user(name: str, password: str, db: Session, is_admin: bool = False) -> User:
    """
    Creates and commits a new user object to the database

    Args:
        name: The name of the user
        password: The plaintext password
        db: The active db session
        is_admin: Whether the user is a admin, defaults to false

    Returns:
        The newly created user.
    """
    hashed_pw = hash_password(password)
    user = User(username=name, password=hashed_pw, is_admin=is_admin)
    db.add(user)
    db.commit()
    return user


def create_post(text: str, owner: User, db: Session) -> Post:
    post = Post(text=text, owner=owner)
    db.add(post)
    db.commit()
    return post
