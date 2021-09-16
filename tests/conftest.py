import os
from typing import Callable, Dict

import pytest
from async_asgi_testclient import TestClient
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_login import LoginManager


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
        'john@doe.com': User(
            name="John",
            surname="Doe",
            email="john@doe.com",
            password="hunter2"
        ),
        'sandra@johnson.com': User(
            name='Sandra',
            surname='Johnson',
            email='sandra@johnson.com',
            password='sandra1243'
        )
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
def secret() -> str:
    return os.urandom(24).hex()


@pytest.fixture(scope="session")
def token_url() -> str:
    return "/auth/token"


@pytest.fixture(scope='module')
def client(app) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def default_data(db) -> dict:
    return {'sub': list(db.keys())[0]}


@pytest.fixture()
def invalid_data() -> dict:
    return {"username": "invalid@e.mail", "password": "invalid-pw"}


@pytest.fixture()
def clean_manager(secret, token_url) -> LoginManager:
    """ Return a new LoginManager instance """
    return LoginManager(secret, token_url)


class CustomAuthException(Exception):
    pass


@pytest.fixture
def custom_exception():
    return CustomAuthException
