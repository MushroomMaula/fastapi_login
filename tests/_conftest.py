import os

from fastapi import FastAPI
from async_asgi_testclient import TestClient
import pytest


@pytest.fixture(scope="module")
def app():
    _app = FastAPI()
    yield _app


@pytest.fixture
def db():
    return {
        'john@doe.com': {
            'name': 'John',
            'surname': 'Doe',
            'email': 'john@doe.com',
            'password': 'hunter2'
        },

        'sandra@johnson.com': {
            'name': 'Sandra',
            'surname': 'Johnson',
            'email': 'sandra@johnson.com',
            'password': 'sandra1243'
        }
    }


@pytest.fixture
def load_user_fn(db: dict):
    def load_user(email: str):
        return db.get(email)

    return load_user


@pytest.fixture
def secret():
    return os.urandom(24).hex


@pytest.fixture
def token_url():
    return "/auth/token"


@pytest.fixture(scope='session')
def client() -> TestClient:
    return TestClient(app)
