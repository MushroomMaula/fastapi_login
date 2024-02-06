import pytest
from fastapi import Depends, Security
from pytest_lazyfixture import lazy_fixture

from fastapi_login import LoginManager


@pytest.fixture(scope="module")
def header_manager(app, secret, token_url, load_user_fn) -> LoginManager:
    instance = LoginManager(secret, token_url)
    instance.user_loader()(load_user_fn)

    @app.get("/private/header")
    def private_header_route(_=Depends(instance)):
        return {"detail": "Success"}

    return instance


@pytest.fixture(scope="module")
def cookie_manager(app, secret, token_url, load_user_fn) -> LoginManager:
    instance = LoginManager(secret, token_url, use_cookie=True, use_header=False)
    instance.user_loader()(load_user_fn)

    @app.get("/private/cookie")
    def private_cookie_route(_=Depends(instance)):
        return {"detail": "Success"}

    return instance


@pytest.fixture(scope="module")
def cookie_header_manager(app, secret, token_url, load_user_fn) -> LoginManager:
    instance = LoginManager(secret, token_url, use_cookie=True)
    instance.user_loader()(load_user_fn)

    @app.get("/private/both")
    def private_route(_=Depends(instance)):
        return {"detail": "Success"}

    @app.get("/private/optional")
    def optional_user_route(user=Depends(instance.optional), invalid: int = 0):
        if user is None and invalid == 1:
            return {"detail": "Success"}
        elif user is not None and invalid == 0:
            return {"detail": "Success"}
        else:
            return {"detail": "Error"}

    return instance


@pytest.fixture(scope="module")
def scoped_manager(app, secret, token_url, load_user_fn) -> LoginManager:
    instance = LoginManager(secret, token_url)
    instance.user_loader()(load_user_fn)

    @app.get("/private/scoped")
    def private_scoped_route(_=Security(instance, scopes=["read"])):
        return {"detail": "Success"}

    return instance


@pytest.mark.asyncio
async def test_header_dependency(client, header_manager, default_data):
    token = header_manager.create_access_token(data=default_data)
    resp = await client.get(
        "/private/header", headers={"Authorization": f"Bearer {token}"}
    )

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Success"


@pytest.mark.asyncio
async def test_cookie_dependency(client, cookie_manager, default_data):
    token = cookie_manager.create_access_token(data=default_data)
    resp = await client.get(
        "/private/cookie", cookies={cookie_manager.cookie_name: token}
    )

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Success"


@pytest.mark.asyncio
async def test_cookie_header_fallback(client, cookie_header_manager, default_data):
    token = cookie_header_manager.create_access_token(data=default_data)
    resp = await client.get(
        "/private/both", headers={"Authorization": f"Bearer {token}"}, cookies={}
    )

    # even tough no valid access cookie is present,
    # as use_header is enabled the request is valid
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Success"


@pytest.mark.asyncio
async def test_scoped_dependency(client, scoped_manager, default_data):
    token = scoped_manager.create_access_token(data=default_data, scopes=["read"])
    resp = await client.get(
        "/private/scoped", headers={"Authorization": f"Bearer {token}"}
    )

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Success"


@pytest.mark.asyncio
async def test_scoped_dependency_raises(client, scoped_manager, default_data):
    token = scoped_manager.create_access_token(data=default_data)
    resp = await client.get(
        "/private/scoped", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "data, is_invalid",
    [(lazy_fixture("default_data"), 0), (lazy_fixture("invalid_data"), 1)],
)
async def test_optional_dependency(client, cookie_header_manager, data, is_invalid):
    token = cookie_header_manager.create_access_token(data=data)
    resp = await client.get(
        "/private/optional",
        headers={"Authorization": f"Bearer {token}"},
        query_string={"invalid": is_invalid},
    )

    assert resp.status_code == 200
    assert resp.json()["detail"] == "Success"
