import secrets
from typing import Callable, Dict

import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_login import LoginManager

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    _has_cryptography = True

    def generate_rsa_key(key_size=2048, password=None):

        key = rsa.generate_private_key(
            backend=default_backend(), public_exponent=65537, key_size=key_size
        )
        private_key = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.BestAvailableEncryption(password)
            if password is not None
            else serialization.NoEncryption(),
        )
        return private_key

except ImportError:
    _has_cryptography = False
    generate_rsa_key = lambda *args, **kwargs: b""


require_cryptography = pytest.mark.skipif(
    not _has_cryptography, reason="Cryptography Not Installed."
)


class User(BaseModel):
    name: str
    surname: str
    email: str
    password: str


@pytest.fixture(scope="module")
def app():
    _app = FastAPI()
    yield _app


@pytest.fixture(scope="session")
def db() -> Dict[str, User]:
    return {
        "john@doe.com": User(
            name="John", surname="Doe", email="john@doe.com", password="hunter2"
        ),
        "sandra@johnson.com": User(
            name="Sandra",
            surname="Johnson",
            email="sandra@johnson.com",
            password="sandra1243",
        ),
    }


@pytest.fixture(scope="session")
def load_user_fn(db: dict) -> Callable[[str], User]:
    def load_user(email: str):
        return db.get(email)

    return load_user


@pytest.fixture(scope="session")
def load_user_fn_with_args() -> Callable[[str, Dict[str, User]], User]:
    def load_user(email: str, db: Dict[str, User]):
        return db.get(email)

    return load_user


@pytest.fixture(scope="session")
def secret():
    return secrets.token_hex(16)


@pytest.fixture(
    scope="session",
    params=[
        pytest.param((secrets.token_hex(16), "HS256")),
        pytest.param((generate_rsa_key(512), "RS256"), marks=require_cryptography),
    ],
)
def secret_and_algorithm(request) -> str:
    return request.param


@pytest.fixture(scope="session")
def token_url() -> str:
    return "/auth/token"


@pytest.fixture(scope="module")
def client(app) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def default_data(db) -> dict:
    return {"sub": list(db.keys())[0]}


@pytest.fixture()
def invalid_data() -> dict:
    return {"username": "invalid@e.mail", "password": "invalid-pw"}


@pytest.fixture()
def clean_manager(secret_and_algorithm, token_url) -> LoginManager:
    """Return a new LoginManager instance"""
    secret, algorithm = secret_and_algorithm
    return LoginManager(secret, token_url, algorithm)


class CustomAuthException(Exception):
    pass


@pytest.fixture
def custom_exception():
    return CustomAuthException
