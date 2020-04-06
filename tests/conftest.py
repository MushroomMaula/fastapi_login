from asyncio import get_event_loop

import pytest
from fastapi import FastAPI


@pytest.fixture(scope='session')
def app():
    return FastAPI()


@pytest.yield_fixture(scope="session")
def event_loop():
    loop = get_event_loop()
    yield loop
    loop.close()
