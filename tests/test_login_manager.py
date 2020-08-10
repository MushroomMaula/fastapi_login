import pytest
from fastapi import HTTPException

from fastapi_login.exceptions import InvalidCredentialsException
from tests.app import load_user, manager, fake_db, TOKEN_URL, NotAuthenticatedException


async def async_load_user(email):
    return load_user(email)


# TESTS

@pytest.mark.asyncio
@pytest.mark.parametrize('function', [load_user, async_load_user])
async def test_user_loader(function, client, default_token):

    # set user loader callback
    manager.user_loader(function)

    user = await manager.get_current_user(default_token)
    assert user['email'] == 'john@doe.com'
    assert user == fake_db['john@doe.com']


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
async def test_bad(data):
    bad_token = manager.create_access_token(
        data=data
    )
    with pytest.raises(Exception):
        try:
            await manager.get_current_user(bad_token)
        except HTTPException:
            raise Exception
        else:
            # test failed
            assert False


@pytest.mark.asyncio
async def test_no_user_callback(default_token):
    manager._user_callback = None
    with pytest.raises(Exception):
        try:
            await manager.get_current_user(default_token)
        except HTTPException:
            raise Exception
        else:
            assert False

    manager.user_loader(load_user)


@pytest.mark.asyncio
async def test_protector(client, default_token):
    response = await client.get(
        '/protected',
        headers={'Authorization': f'Bearer {default_token}'}
    )
    assert response.json()['status'] == 'Success'


@pytest.mark.asyncio
async def test_cookie_protector(client):
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
async def test_not_authenticated_exception(client):
    manager.not_authenticated_exception = NotAuthenticatedException
    resp = await client.get(
        '/protected'
    )
    assert resp.json()['data'] == 'redirected'
