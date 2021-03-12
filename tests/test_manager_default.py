import pytest
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException


@pytest.fixture
def manager(app, secret, token_url, load_user_fn):
    instance = LoginManager(secret, token_url)
    instance.user_loader(load_user_fn)

    @app.post(token_url)
    def login(data: OAuth2PasswordRequestForm = Depends()):
        user_identifier = data.username
        password = data.password

        user = load_user_fn(user_identifier)
        if not user:
            raise InvalidCredentialsException
        elif password != user['password']:
            raise InvalidCredentialsException

        access_token = manager.create_access_token(
            data=dict(sub=user_identifier)
        )

        return {'access_token': access_token, 'token_type': 'Bearer'}

    @app.get("/private")
    def private_route(_=Depends(instance)):
        return {"detail": "Success"}


