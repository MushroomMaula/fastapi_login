from fastapi_login import LoginManager

from app.config import Config

manager = LoginManager(Config.secret, Config.token_url)


def hash_password(plaintext: str):
    """
    Hashes the plaintext password using bcrypt

    Args:
        plaintext: The password in plaintext

    Returns:
        The hashed password, including salt and algorithm information
    """
    return manager.pwd_context.hash(plaintext)


def verify_password(plaintext: str, hashed: str):
    """
    Checks the plaintext password against the provided hashed password

    Args:
        plaintext: The password as provided by the user
        hashed: The password as stored in the db

    Returns:
        True if the passwords match
    """

    return manager.pwd_context.verify(plaintext, hashed)
