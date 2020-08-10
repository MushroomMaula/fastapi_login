import inspect
import typing
from datetime import timedelta, datetime
from typing import Callable, Awaitable, Union

import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext
from starlette.datastructures import Secret
from starlette.requests import Request

from fastapi_login.exceptions import InvalidCredentialsException


class LoginManager(OAuth2PasswordBearer):

    def __init__(self, secret: str, tokenUrl: str, algorithm="HS256", use_cookie=False):
        """
        :param str secret: Secret key used to sign and decrypt the JWT
        :param str algorithm: Should be "HS256" or "RS256" used to decrypt the JWT
        :param str tokenUrl: the url where the user can login to get the token
        """
        self.secret = Secret(secret)
        self._user_callback = None
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"])
        # this is not mandatory as they user may want to user their own
        # function to get the token and pass it to the get_current_user method
        self.tokenUrl = tokenUrl
        self.oauth_scheme = None
        self._not_authenticated_exception = None

        self.use_cookie = use_cookie
        self.cookie_name = 'access-token'

        super().__init__(tokenUrl=tokenUrl, auto_error=True)

    def user_loader(self, callback: Union[Callable, Awaitable]) -> Union[Callable, Awaitable]:
        """
        This sets the callback to retrieve the user.
        The function should take an unique identifier like an email
        and return the user object or None.

        Basic usage::

            >>> from fastapi import FastAPI
            >>> from fastapi_login import LoginManager

            >>> app = FastAPI()
            >>> # use import os; print(os.urandom(24).hex()) to get a true secret key
            >>> SECRET = "super-secret"

            >>> manager = LoginManager(SECRET, tokenUrl="Login")

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

    @property
    def not_authenticated_exception(self):
        return self._not_authenticated_exception

    @not_authenticated_exception.setter
    def not_authenticated_exception(self, value: Exception):
        """
        Setter for the Exception which raises when the user is not authenticated

        :param Exception value: The Exception you want to raise
        """
        assert issubclass(value, Exception)
        self._not_authenticated_exception = value
        # change auto error setting on OAuth2PasswordBearer
        self.auto_error = False

    async def get_current_user(self, token: str):
        """
        This decodes the jwt based on the secret and on the algorithm
        set on the LoginManager.
        If the token is correctly formatted and the user is found
        the user is returned else this raises a `fastapi.HTTPException`

        :param str token: The encoded jwt token
        :return: The user object returned by `self._user_callback`
        :raise: HTTPException if the token is invalid or the user is not found
        """
        try:
            payload = jwt.decode(
                token,
                str(self.secret),
                algorithms=[self.algorithm]
            )
            # the identifier should be stored under the sub (subject) key
            user_identifier = payload.get('sub')
            if user_identifier is None:
                raise InvalidCredentialsException
        except jwt.PyJWTError:
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
        :raises: Exception if the user_back has not been set
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

    def create_access_token(self, *, data: dict, expires_delta: timedelta = None) -> str:
        """
        Helper function to create the encoded access token using
        the provided secret and the algorithm of the LoginManager instance

        :param dict data: The data which should be stored in the token
        :param  timedelta expires_delta: An optional timedelta in which the token expires.
            Defaults to 15 minutes
        :return: The encoded JWT with the data and the expiry. The expiry is
            available under the 'exp' key
        """

        to_encode = data.copy()

        if expires_delta:
            expires_in = datetime.utcnow() + expires_delta
        else:
            # default to 15 minutes expiry times
            expires_in = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({'exp': expires_in})
        encoded_jwt = jwt.encode(to_encode, str(self.secret), self.algorithm)
        # decode here decodes the bytestr to a normal str not the token
        return encoded_jwt.decode()

    def _token_from_cookie(self, request: Request) -> typing.Optional[str]:
        """
        Checks the requests cookies for the cookie with the name `self.cookie_name`

        :return: The access token found in the cookies of the request or none
        """
        auth = request.cookies.get(self.cookie_name)
        _, token = get_authorization_scheme_param(auth)

        if not token and self.auto_error:
            # this is the standard exception as raised
            # by the parent class
            raise InvalidCredentialsException

        else:
            return token

    async def __call__(self, request: Request):
        """
        Provides the functionality to act as a Dependency

        :param Request request: The incoming request, this is set automatically
            by FastAPI
        :return: The user object or None
        :raises: The not_authenticated_exception if set by the user
        """
        if self.use_cookie:
            token = self._token_from_cookie(request)
        else:
            token = await super(LoginManager, self).__call__(request)

        if token is not None:
            return await self.get_current_user(token)

        # No token is present in the request and no Exception has been raised (auto_error=False)
        raise self.not_authenticated_exception
