import time
from datetime import timedelta
from http.cookies import SimpleCookie
from unittest.mock import Mock, AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import SecurityScopes
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
    clean_manager.user_loader()(loader)
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
    clean_manager.user_loader()(load_user_fn)
    token = clean_manager.create_access_token(data={"sub": invalid_data["username"]})
    with pytest.raises(HTTPException) as exc_info:
        await clean_manager.get_current_user(token)

    assert exc_info.value == InvalidCredentialsException


@pytest.mark.asyncio
async def test_user_loader_with_arguments(clean_manager, default_data, load_user_fn_with_args, db):
    token = clean_manager.create_access_token(data=default_data)
    loader = Mock()
    clean_manager.user_loader(db)(loader)
    _ = await clean_manager.get_current_user(token)

    loader.assert_called()
    loader.assert_called_with(default_data['sub'], db)


@pytest.mark.asyncio
async def test_user_loader_decorator_syntax_no_args(clean_manager, default_data):

    @clean_manager.user_loader()
    def load_user(email: str):
        return default_data["sub"]

    token = clean_manager.create_access_token(data=default_data)
    result = await clean_manager.get_current_user(token)
    assert result == default_data["sub"]


@pytest.mark.asyncio
async def test_user_loader_decorator_syntax_no_args_backwards_compatible(clean_manager, default_data):

    @clean_manager.user_loader
    def load_user(email: str):
        return default_data["sub"]

    token = clean_manager.create_access_token(data=default_data)
    result = await clean_manager.get_current_user(token)
    assert result == default_data["sub"]


def test_user_loader_backwards_compatible_syntax_warns(clean_manager, load_user_fn):
    with pytest.warns(SyntaxWarning) as record:
        @clean_manager.user_loader
        def fn(sub):
            pass

        clean_manager.user_loader(load_user_fn)

    # A SyntaxWarning should be issued both times
    assert len(record) == 2


def test_user_loader_still_callable(clean_manager):
    checker = Mock()

    @clean_manager.user_loader
    def fn():
        checker()
        return
    assert callable(fn)
    # assure that the method we return is actually the same
    fn()
    assert checker.call_count == 1

    @clean_manager.user_loader()
    def fn():
        checker()
        return

    assert callable(fn)
    fn()
    assert checker.call_count == 2


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


def test_has_scopes_true(clean_manager, default_data):
    scopes = ["read"]
    token = clean_manager.create_access_token(data=default_data, scopes=scopes)
    required_scopes = SecurityScopes(scopes=scopes)
    assert clean_manager.has_scopes(token, required_scopes)


def test_has_scopes_no_scopes(clean_manager, default_data):
    scopes = ["read"]
    token = clean_manager.create_access_token(data=default_data)
    assert clean_manager.has_scopes(token, SecurityScopes(scopes=scopes)) is False


def test_has_scopes_missing_scopes(clean_manager, default_data):
    scopes = ["read"]
    default_data["scopes"] = scopes
    token = clean_manager.create_access_token(data=default_data)
    required_scopes = ["write"]
    assert clean_manager.has_scopes(token, SecurityScopes(scopes=required_scopes)) is False
    required_scopes = scopes + ["write"]
    assert clean_manager.has_scopes(token, SecurityScopes(scopes=required_scopes)) is False


def test_has_scopes_invalid_token(clean_manager):
    token = "invalid-token"
    assert not clean_manager.has_scopes(token, SecurityScopes(scopes=["test"]))


def test_has_scopes_which_are_not_required(clean_manager, default_data):
    scopes = ["read", "write"]
    required_scopes = ["read"]
    default_data["scopes"] = scopes
    token = clean_manager.create_access_token(data=default_data)
    assert clean_manager.has_scopes(token, SecurityScopes(scopes=required_scopes))
