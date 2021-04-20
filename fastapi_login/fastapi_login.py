import inspect
import typing
from datetime import timedelta, datetime
from typing import Callable, Awaitable, Union

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette.datastructures import Secret

from fastapi import FastAPI, Request, Response

from fastapi_login.exceptions import InvalidCredentialsException


class LoginManager(OAuth2PasswordBearer):
    """
    Attributes:
        secret (starlette.datastructures.Secret): The secret used to sign and decrypt the JWT
        algorithm (str): The algorithm used to decrypt the token defaults to ``HS256``
        token_url (str): The url where the user can login to get the token
        use_cookie (bool): Whether cookies should be checked for the token
        use_header (bool): Whether headers should be checked for the token
        pwd_context (passlib.CryptContext): Instance of ``passlib.CryptContext`` using bcrypt for
            convenient access to hashing and verifying passwords.
        cookie_name (str): The name of the cookie checked for the token, defaults to `"access-token"`
    """

    def __init__(self, secret: str, token_url: str, algorithm="HS256", use_cookie=False, use_header=True):
        """
        Initializes LoginManager

        Args:
            algorithm (str): Should be "HS256" or "RS256" used to decrypt the JWT
            token_url (str): The url where the user can login to get the token
            use_cookie (bool): Set if cookies should be checked for the token
            use_header (bool): Set if headers should be checked for the token
        """
        if use_cookie is False and use_header is False:
            raise Exception("use_cookie and use_header are both False one of them needs to be True")
        self.secret = Secret(secret)
        self._user_callback = None
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"])
        self.tokenUrl = token_url
        self.oauth_scheme = None
        self._not_authenticated_exception = InvalidCredentialsException

        self.use_cookie = use_cookie
        self.use_header = use_header
        self.cookie_name = 'access-token'

        super().__init__(tokenUrl=token_url, auto_error=True)

    @property
    def not_authenticated_exception(self):
        """
        Exception raised when no (valid) token is present.
        Defaults to `fastapi_login.exceptions.InvalidCredentialsException`
        """
        return self._not_authenticated_exception

    @not_authenticated_exception.setter
    def not_authenticated_exception(self, value: Exception):
        """
        Setter for the Exception which raises when the user is not authenticated.
        Sets `self.auto_error` to False in order to raise the correct exception.

        Args:
            value (Exception): The Exception you want to raise
        """
        assert issubclass(value, Exception)  # noqa
        self._not_authenticated_exception = value
        # change auto error setting on OAuth2PasswordBearer
        self.auto_error = False

    def user_loader(self, callback: Union[Callable, Awaitable]) -> Union[Callable, Awaitable]:
        """
        This sets the callback to retrieve the user.
        The function should take an unique identifier like an email
        and return the user object or None.

        Basic usage:

            >>> from fastapi import FastAPI
            >>> from fastapi_login import LoginManager

            >>> app = FastAPI()
            >>> # use import os; print(os.urandom(24).hex()) to get a true secret key
            >>> SECRET = "super-secret"

            >>> manager = LoginManager(SECRET, token_url="Login")

            >>> manager.user_loader(get_user)

            >>> @manager.user_loader
            >>> def get_user():
            ...     # get user logic here

        Args:
            callback (Callable or Awaitable): The callback which returns the user

        Returns:
            The callback
        """
        self._user_callback = callback
        return callback

    async def get_current_user(self, token: str):
        """
        This decodes the jwt based on the secret and on the algorithm
        set on the LoginManager.
        If the token is correctly formatted and the user is found
        the user is returned else this raises `LoginManager.not_authenticated_exception`

        Args:
            token (str): The encoded jwt token

        Returns:
            The user object returned by the instances `_user_callback`

        Raises:
            LoginManager.not_authenticated_exception: The token is invalid or None was returned by `_load_user`
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
                raise self.not_authenticated_exception
        # This includes all errors raised by pyjwt
        except jwt.PyJWTError:
            raise self.not_authenticated_exception

        user = await self._load_user(user_identifier)

        if user is None:
            raise self.not_authenticated_exception

        return user

    async def _load_user(self, identifier: typing.Any):
        """
        This loads the user using the user_callback

        Args:
            identifier (Any): The user identifier expected by `_user_callback`

        Returns:
            The user object returned by `_user_callback` or None

        Raises:
            Exception: The user_loader has not been set
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

    def create_access_token(self, *, data: dict, expires: timedelta = None) -> str:
        """
        Helper function to create the encoded access token using
        the provided secret and the algorithm of the LoginManager instance

        Args:
            data (dict): The data which should be stored in the token
            expires (datetime.timedelta):  An optional timedelta in which the token expires.
                Defaults to 15 minutes

        Returns:
            The encoded JWT with the data and the expiry. The expiry is
            available under the 'exp' key
        """

        to_encode = data.copy()

        if expires:
            expires_in = datetime.utcnow() + expires
        else:
            # default to 15 minutes expiry times
            expires_in = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({'exp': expires_in})
        encoded_jwt = jwt.encode(to_encode, str(self.secret), self.algorithm)
        # decode here decodes the byte str to a normal str not the token
        return encoded_jwt

    def set_cookie(self, response: Response, token: str) -> None:
        """
        Utility function to set a cookie containing token on the response

        Args:
            response (fastapi.Response): The response which is send back
            token (str): The created JWT
        """
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            httponly=True
        )

    def _token_from_cookie(self, request: Request) -> typing.Optional[str]:
        """
        Checks the requests cookies for cookies with the name `self.cookie_name`

        Args:
            request (fastapi.Request):  The request to the route, normally filled in automatically

        Returns:
            The access token found in the cookies of the request or None

        Raises:
            LoginManager.not_authenticated_exception: No cookie with name ``LoginManager.cookie_name``
                is set on the Request
        """
        token = request.cookies.get(self.cookie_name)

        # we dont use `token is None` in case a cookie with self.cookie_name
        # exists but is set to "", in which case `token is None` evaluates to False
        if not token and self.auto_error:
            # either default InvalidCredentialsException or set by user
            raise self.not_authenticated_exception

        else:
            # Token may be "" so we convert to None
            return token if token else None

    async def __call__(self, request: Request):
        """
        Provides the functionality to act as a Dependency

        Args:
            request (fastapi.Request):The incoming request, this is set automatically
                by FastAPI

        Returns:
            The user object or None

        Raises:
            LoginManager.not_authenticated_exception: If set by the user and `self.auto_error` is set to False

        """
        token = None
        try:
            if self.use_cookie:
                token = self._token_from_cookie(request)
        # The Exception is either a InvalidCredentialsException
        # or a custom exception set by the user
        except Exception as e:
            # In case use_cookie and use_header is enabled
            # headers should be checked if cookie lookup fails
            if self.use_header:
                pass
            else:
                raise e

        if token is None and self.use_header:
            token = await super(LoginManager, self).__call__(request)

        if token is None:
            # No token is present in the request and no Exception has been raised (auto_error=False)
            raise self.not_authenticated_exception
        else:
            return await self.get_current_user(token)

    def useRequest(self, app: FastAPI):
        """
        Add the instance as a middleware, which adds the user object, if present,
        to the request state

        Args:
            app (fastapi.FastAPI): A instance of FastAPI
        """
        @app.middleware("http")
        async def user_middleware(request: Request, call_next):
            try:
                request.state.user = await self.__call__(request)
            except Exception as e:
                # An error occurred while getting the user
                # as middlewares are called for every incoming request
                # it's not a good idea to return the Exception
                # so we set the user to None
                request.state.user = None
            
            return await call_next(request)
