import inspect
import typing
from datetime import timedelta, datetime
from typing import Callable, Awaitable, Union

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette.applications import Starlette
from starlette.requests import Request

from fastapi_login.exceptions import InvalidCredentialsException


def is_setup_correctly(app: Starlette) -> bool:
    """
    This checks if the app has the config attribute.
    :param Starlette app: The app instance
    :return: True if the app has a config attribute else False
    """
    if not hasattr(app, 'config'):
        return False
    return True


class LoginManager:

    def __init__(self, app: Starlette, tokenUrl: str = None, algorithm="HS256"):
        """
        :param Starlette app: An instance or subclass of `Starlette`
        :param str algorithm: Should be "HS256" or "RS256" used to decrypt the JWT
        :param str tokenUrl: the url where the user can login to get the token
        """
        self._user_callback = None
        self.app = app
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"])
        # this is not mandatory as they user may want to user their own
        # function to get the token and pass it to the get_current_user method
        self.tokenUrl = tokenUrl
        self.oauth_scheme = None
        self._protector = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Starlette):
        """
        Adds this LoginManager instance to the app as attribute.

        :param Starlette app: An instance of subclass of Starlette
        """
        if not is_setup_correctly(app):
            raise Exception(
                "Setup your app config as explained in the docs!"
            )
        setattr(app, 'login_manager', self)

    def user_loader(self, callback: Union[Callable, Awaitable]) -> Union[Callable, Awaitable]:
        """
        This sets the callback to retrieve the user.
        The function should take an unique identifier like an email
        and return the user object or None.

        Basic usage::

            >>> from fastapi import FastAPI
            >>> from fastapi_login import LoginManager

            >>> app = FastAPI()
            >>> # setup the app config
            >>> app.config = {}

            >>> manager = LoginManager(app)

            >>> manager.user_loader(get_user)

            >>> # this is the preferred way
            >>> @manager.user_loader
            >>> def get_user():
            ...     # get user logic here

        :param Callable or Awaitable callback: The callback which returns the user
        :return: The callback
        """
        self._user_callback = callback
        return callback

    async def get_current_user(self, token: str):
        """
        This decodes the jwt based on the secret set in the app config
        and on the algorithm set on the LoginManager.
        If the token is correctly formatted and the user is found
        the user is returned else this raises a `fastapi.HTTPException`

        :param str token: The encoded jwt token
        :return: The user object returned by `self._user_callback`
        :raise: HTTPException if the token is invalid or the user is not found
        """
        try:
            payload = jwt.decode(
                token,
                str(self.app.config['secret']),
                algorithms=[self.algorithm]
            )
            # the identifier should be stored under the sub (subject) key
            user_identifier = payload.get('sub')
            if user_identifier is None:
                raise InvalidCredentialsException
        except jwt.PyJWTError as e:
            raise InvalidCredentialsException

        user = await self._load_user(user_identifier)

        if user is None:
            raise InvalidCredentialsException

        return user

    async def _load_user(self, identifier: typing.Any):
        """
        This loads the user using the user_callback

        :param typing.Any identifier: The identifier the user callback takes
        :return: The user object or None
        :raise: Exception if the user_back has not been set
        """
        if self._user_callback is None:
            raise Exception(
                "Missing user_loader callback"
            )

        if inspect.iscoroutinefunction(self._user_callback):
            user = await self._user_callback(identifier)
        else:
            user = self._user_callback(identifier)

        return user

    def create_access_token(self, *, data: dict, expires_delta: timedelta = None) -> dict:
        """
        Helper function to create the encoded access token using the secret
        set in the app config and the algorithm of the LoginManager instance

        :param dict data: The data which should be stored in the token
        :param  timedelta expires_delta: An optional timedelta in which the token expires.
            Defaults to 15 minutes can be set using the parameter
             or the `TOKEN_EXPIRY` key in the app config
        :return: The encoded JWT with the data and the expiry. The expiry is
            available under the 'exp' key
        """

        to_encode = data.copy()

        if expires_delta:
            expires_in = datetime.utcnow() + expires_delta
        else:
            # check if the expiry has been changed using the config
            expiry = self.app.config.get('TOKEN_EXPIRY')
            if expiry:
                expires_in = datetime.utcnow() + expiry
            else:
                # default to 15 minutes expiry times
                expires_in = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({'exp': expires_in})
        encoded_jwt = jwt.encode(to_encode, str(self.app.config['secret']), self.algorithm)
        return encoded_jwt.decode()

    async def __call__(self, request: Request):
        if not self.tokenUrl:
            raise Exception(
                "You need to set the tokenUrl first!"
            )

        if self.oauth_scheme is None:
            self.oauth_scheme = OAuth2PasswordBearer(tokenUrl=self.tokenUrl)

        token = await self.oauth_scheme(request)
        return await self.get_current_user(token)
