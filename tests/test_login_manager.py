import time
from datetime import timedelta
from http.cookies import SimpleCookie
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from starlette.responses import Response

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from tests.app import load_user, manager, fake_db, TOKEN_URL, NotAuthenticatedException, cookie_manager


async def async_load_user(email):
    return load_user(email)


# TESTS
@pytest.mark.asyncio
async def test_token_expiry(default_data):
    token = manager.create_access_token(
        data=default_data,
        expires=timedelta(microseconds=1)  # should be invalid instantly
    )
    time.sleep(1)
    with pytest.raises(HTTPException):
        await manager.get_current_user(token)

@pytest.mark.asyncio
@pytest.mark.parametrize('function', [load_user, async_load_user])
async def test_user_loader(function, client, default_token):
    # set user loader callback
    manager.user_loader(function)

    user = await manager.get_current_user(default_token)
    assert user['email'] == 'john@doe.com'
    assert user == fake_db['john@doe.com']

@pytest.mark.asyncio
async def test_user_loader_returns_none(client, invalid_user_token):
    with pytest.raises(HTTPException):
        await manager.get_current_user(invalid_user_token)


@pytest.mark.asyncio
async def test_bad_credentials(client):
    response = await client.post('/auth/token', form=dict(username='invald@e.mail', password='invalidpw'))
    assert response.status_code == 401
    assert response.json()['detail'] == InvalidCredentialsException.detail


@pytest.mark.asyncio
@pytest.mark.parametrize('data', [
    {'invalid': 'token-format'},
    {'sub': 'invalid-username'}
])
async def test_bad_data(data):
    bad_token = manager.create_access_token(
        data=data
    )
    with pytest.raises(HTTPException):
        await manager.get_current_user(bad_token)


@pytest.mark.asyncio
async def test_no_user_callback(default_token):
    manager._user_callback = None
    with pytest.raises(Exception):
        await manager.get_current_user(default_token)

    manager.user_loader(load_user)


@pytest.mark.asyncio
async def test_dependency_functionality(client, default_token):
    response = await client.get(
        '/protected',
        headers={'Authorization': f'Bearer {default_token}'}
    )
    assert response.json()['status'] == 'Success'


@pytest.mark.asyncio
async def test_cookie_checking(client):
    cookie_resp = await client.post(
        TOKEN_URL, query_string={'cookie': True},
        form=dict(username='john@doe.com', password='hunter2')
    )

    response = await client.get(
        '/protected/cookie',
        cookies=cookie_resp.cookies
    )

    assert response.json()['status'] == 'Success'


@pytest.mark.asyncio
@pytest.mark.parametrize('data', [
    (manager, '/protected'),
    (cookie_manager, '/protected/cookie')
])
async def test_not_authenticated_exception(data, client):
    curr_manager, url = data
    curr_manager.not_authenticated_exception = NotAuthenticatedException
    # cookie_jar is persisted from tests before -> clear
    client.cookie_jar = SimpleCookie()
    resp = await client.get(
        url
    )
    assert resp.json()['data'] == 'redirected'


@pytest.mark.asyncio
async def test_request_state_user_unauthorized(client):
    resp = await client.get(
        '/protected/request'
    )
    assert resp.json()['status'] == 'Unauthorized'


@pytest.mark.asyncio
async def test_request_state_user(client, default_token):
    resp = await client.get(
        '/protected/request',
        headers={'Authorization': f'Bearer {default_token}'}
    )
    assert resp.json()['status'] == 'Success'

def test_token_from_cookie_return():
    m = Mock(cookies={'access-token': ''})

    cookie = manager._token_from_cookie(m)
    assert cookie is None

def test_token_from_cookie_exception():
    # reset from tests before, asssume no custom exception has been set
    manager.auto_error = True
    m = Mock(cookies={'access-token': ''})
    with pytest.raises(HTTPException):
        manager._token_from_cookie(m)


def test_set_cookie(default_token):
    response = Response()
    manager.set_cookie(response, default_token)
    assert response.headers['set-cookie'].startswith(f"{manager.cookie_name}={default_token}")


def test_no_cookie_and_no_header_exception():
    with pytest.raises(Exception):
        LoginManager('secret', 'login', use_cookie=False, use_header=False)

@pytest.mark.asyncio
async def test_cookie_header_fallback(client, default_token):
    cookie_manager.use_header = True
    resp = await client.get(
        '/protected/cookie',
        headers={'Authorization': f'Bearer {default_token}'}
    )
    assert resp.json()['status'] == 'Success'
