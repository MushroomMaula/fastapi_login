import os

import pytest
from async_asgi_testclient import TestClient
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException

fake_db = {
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

app = FastAPI()
client = TestClient(app)
SECRET = os.urandom(24).hex()
lm = LoginManager(SECRET, app, tokenUrl='/auth/token')


@app.post('/auth/token')
def login(data: OAuth2PasswordRequestForm = Depends()):
    user_identifier = data.username
    password = data.password

    user = load_user(user_identifier)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException

    access_token = lm.create_access_token(
        data=dict(sub=user_identifier)
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


@app.post('/protected', dependencies=[Depends(lm)])
def protected_route():
    return {'status': 'Success'}


def load_user(email: str):
    user = fake_db.get(email)
    if not user:
        return None

    return user


async def async_load_user(email):
    return load_user(email)


# TESTS

@pytest.mark.asyncio
@pytest.mark.parametrize('function', [load_user, async_load_user])
async def test_user_loader(function):

    # set user loader callback
    lm.user_loader(function)

    response = await client.post('/auth/token', form=dict(username='john@doe.com', password='hunter2'))

    data = response.json()
    token = data['access_token']

    user = await lm.get_current_user(token)
    assert user['email'] == 'john@doe.com'
    assert user == fake_db['john@doe.com']


@pytest.mark.asyncio
async def test_bad_credentials():
    response = await client.post('/auth/token', form=dict(username='invald@e.mail', password='invalidpw'))
    assert response.status_code == 401
    assert response.json()['detail'] == InvalidCredentialsException.detail


@pytest.mark.asyncio
async def test_bad_token_format():
    bad_token = lm.create_access_token(
        data={'invalid': 'token-format'}
    )
    with pytest.raises(Exception):
        try:
            await lm.get_current_user(bad_token)
        except HTTPException:
            raise Exception
        else:
            # test failed
            assert False


@pytest.mark.asyncio
async def test_bad_user_identifier_in_token():
    bad_token = lm.create_access_token(
        data={'sub': 'invalid-username'}
    )

    with pytest.raises(Exception):
        try:
            await lm.get_current_user(bad_token)
        except HTTPException:
            raise Exception
        else:
            # test failed
            assert False


@pytest.mark.asyncio
async def test_no_user_callback():
    manager = LoginManager(SECRET, app)
    token = manager.create_access_token(data=dict(sub='john@doe.com'))
    with pytest.raises(Exception):
        try:
            await manager.get_current_user(token)
        except HTTPException:
            raise Exception
        else:
            assert False


@pytest.mark.asyncio
async def test_protector():
    lm.user_loader(load_user)
    token = lm.create_access_token(
        data={'sub': 'john@doe.com'}
    )
    response = await client.post(
        '/protected',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.json()['status'] == 'Success'


@pytest.mark.asyncio
async def test_protect_tokenUrl_not_set():
    manager = LoginManager(SECRET, app)
    with pytest.raises(Exception):
        await manager(None)

