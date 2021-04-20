from datetime import timedelta
import time
from http.cookies import SimpleCookie
from unittest.mock import Mock, AsyncMock

import pytest
from fastapi import HTTPException
from starlette.responses import Response

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException


@pytest.mark.asyncio
async def test_token_expiry(clean_manager, default_data):
    token = clean_manager.create_access_token(
        data=default_data,
        expires=timedelta(microseconds=1)  # should be invalid instantly
    )
    time.sleep(1)
    with pytest.raises(HTTPException) as exc_info:
        await clean_manager.get_current_user(token)

    assert exc_info


@pytest.mark.asyncio
@pytest.mark.parametrize("loader", [Mock(), AsyncMock()])
async def test_user_loader(loader, clean_manager, default_data, db):
    token = clean_manager.create_access_token(data=default_data)
    loader = Mock()
    clean_manager.user_loader(loader)
    _ = await clean_manager.get_current_user(token)

    loader.assert_called()
    loader.assert_called_with(default_data['sub'])


@pytest.mark.asyncio
async def test_user_loader_not_set(clean_manager, default_data):
    token = clean_manager.create_access_token(data=default_data)
    with pytest.raises(Exception) as exc_info:
        await clean_manager.get_current_user(token)

    assert "Missing user_loader callback" == str(exc_info.value)


@pytest.mark.asyncio
async def test_user_loader_returns_none(clean_manager, invalid_data, load_user_fn):
    clean_manager.user_loader(load_user_fn)
    token = clean_manager.create_access_token(data={"sub": invalid_data["username"]})
    with pytest.raises(HTTPException) as exc_info:
        await clean_manager.get_current_user(token)

    assert exc_info.value == InvalidCredentialsException


def test_token_from_cookie(clean_manager):
    request = Mock(cookies={clean_manager.cookie_name: "test-value"})
    token = clean_manager._token_from_cookie(request)
    assert token == "test-value"


def test_token_from_cookie_raises(clean_manager):
    request = Mock(cookies={clean_manager.cookie_name: ""})
    with pytest.raises(HTTPException) as exc_info:
        clean_manager._token_from_cookie(request)

    assert exc_info.value == InvalidCredentialsException
    
    
def test_token_from_cookie_returns_none_auto_error_off(clean_manager):
    clean_manager.auto_error = False
    request = Mock(cookies={clean_manager.cookie_name: ""})
    token = clean_manager._token_from_cookie(request)
    assert token is None


def test_set_cookie(clean_manager, default_data):
    token = clean_manager.create_access_token(data=default_data)
    response = Response()
    clean_manager.set_cookie(response, token)
    cookie = SimpleCookie(response.headers['set-cookie'])
    cookie_value = cookie.get(clean_manager.cookie_name)
    assert cookie_value is not None
    assert cookie_value["httponly"] is True
    assert cookie_value["samesite"] == "lax"
    assert cookie_value.value == token
    assert cookie_value.key == clean_manager.cookie_name


def test_config_no_cookie_no_header_raises(secret, token_url):
    with pytest.raises(Exception) as exc_info:
        LoginManager(secret, token_url, use_cookie=False, use_header=False)

    assert "use_cookie and use_header are both False one of them needs to be True" == str(exc_info.value)



