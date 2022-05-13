from unittest.mock import Mock

import pytest
from fastapi import Depends
from starlette.responses import RedirectResponse

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException


@pytest.fixture
def exception_manager(app, secret, token_url, load_user_fn, custom_exception) -> LoginManager:
    instance = LoginManager(secret, token_url, custom_exception=custom_exception)
    instance.user_loader()(load_user_fn)

    # exception handling setup

    @app.exception_handler(custom_exception)
    def redirect_on_auth_exc(request, exc):
        return RedirectResponse(url="/redirect")

    # routes
    # Should raise the custom exception when encountering
    # a non-authenticated user and redirect
    @app.get("/private/exception")
    def raise_exception(_=Depends(instance)):
        return {"detail": "error"}

    @app.get("/redirect")
    def redirect():
        return {"detail": "Redirected"}

    return instance


def test_exception_setter_deprecated_warns(clean_manager, custom_exception):
    with pytest.deprecated_call():
        clean_manager.not_authenticated_exception = custom_exception


@pytest.mark.asyncio
async def test_exception_call_cookie_error_user_header_false(clean_manager):
    # setup clean_manager
    clean_manager.use_cookie = True
    clean_manager.use_header = False
    response = Mock(cookies={})
    with pytest.raises(Exception) as exc_info:  # HTTPExceptions cannot be used with pytest.raises
        await clean_manager(response)

    assert exc_info.value is InvalidCredentialsException


@pytest.mark.asyncio
async def test_exception_call_raises_no_token_auto_error_off(clean_manager):
    clean_manager.auto_error = False
    # set headers so fastapi internals dont raise an error
    response = Mock(headers={"abc": "abc"})
    with pytest.raises(Exception) as exc_info:   # HTTPExceptions cannot be used with pytest.raises
        await clean_manager(response)

    assert exc_info.value is InvalidCredentialsException


@pytest.mark.asyncio
async def test_exception_handling(exception_manager, client, invalid_data):
    invalid_token = exception_manager.create_access_token(data={"sub": invalid_data["username"]})
    resp = await client.get(
        "/private/exception",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )

    assert resp.json()["detail"] == "Redirected"


@pytest.mark.asyncio
async def test_exception_handling_with_no_token(exception_manager, client, invalid_data):
    # Set use cookie true for this test to check all possible ways to raise an error
    exception_manager.use_cookie = True
    resp = await client.get(
        "/private/exception"
    )
    assert resp.json()["detail"] == "Redirected"


@pytest.mark.asyncio
async def test_exception_changes_no_sub(exception_manager, custom_exception):
    no_sub_token = exception_manager.create_access_token(data={"id": "something"})
    with pytest.raises(custom_exception) as exc_info:
        await exception_manager.get_current_user(no_sub_token)


@pytest.mark.asyncio
async def test_exception_changes_invalid_token(exception_manager, custom_exception):
    invalid_jwt_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.aGVsb"
        "G8gd29ybGQ.SIr03zM64awWRdPrAM_61QWsZchAtgDV"
        "3pphfHPPWkI"
    )  # this token is taken from pyjwt (https://github.com/jpadilla/pyjwt/blob/master/tests/test_api_jwt.py#L82)
    with pytest.raises(custom_exception) as exc_info:
        await exception_manager.get_current_user(invalid_jwt_token)


@pytest.mark.asyncio
async def test_exception_changes_user_is_none(exception_manager, custom_exception, invalid_data):
    invalid_user_token = exception_manager.create_access_token(data={"sub": invalid_data["username"]})
    with pytest.raises(custom_exception) as exc_info:
        await exception_manager.get_current_user(invalid_user_token)
