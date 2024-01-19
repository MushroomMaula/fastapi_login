from config import DEFAULT_SETTINGS
from passlib.context import CryptContext

from fastapi_login import LoginManager

manager = LoginManager(DEFAULT_SETTINGS.secret, DEFAULT_SETTINGS.token_url)
pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(plaintext_password: str):
    """Return the hash of a password"""
    return pwd_context.hash(plaintext_password)


def verify_password(password_input: str, hashed_password: str):
    """Check if the provided password matches"""
    return pwd_context.verify(password_input, hashed_password)
