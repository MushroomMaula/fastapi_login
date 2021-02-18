from asyncio import get_event_loop

import pytest
from async_asgi_testclient import TestClient

from tests.app import app, manager


@pytest.fixture(scope='session')
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture()
def default_data() -> dict:
    return {'sub': 'john@doe.com'}

@pytest.fixture()
def default_token(default_data) -> str:
    return manager.create_access_token(
        data=default_data
    )

@pytest.fixture()
def invalid_user_token() -> str:
    return manager.create_access_token(
        data={'sub': 'not-a-user-id'}
    )


@pytest.fixture(scope="session")
def event_loop():
    loop = get_event_loop()
    yield loop
    loop.close()
