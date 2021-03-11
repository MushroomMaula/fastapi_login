from fastapi_login import LoginManager

from config import DEFAULT_SETTINGS

manager = LoginManager(DEFAULT_SETTINGS.secret, DEFAULT_SETTINGS.token_url)

def hash_password(plaintext_password: str):
    """ Return the hash of a password """
    return manager.pwd_context.hash(plaintext_password)

def verify_password(password_input: str, hashed_password: str):
    """ Check if the provided password matches """
    return manager.pwd_context.verify(password_input, hashed_password)