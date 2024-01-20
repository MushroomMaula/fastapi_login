import inspect
import typing
import warnings
from datetime import datetime, timedelta, timezone
from typing import Awaitable, Callable, Collection, Dict, Optional, Type, Union

import jwt
from anyio.to_thread import run_sync
from fastapi import FastAPI, Request, Response
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from .exceptions import InvalidCredentialsException
from .secrets import to_secret
from .utils import ordered_partial

SECRET_TYPE = Union[str, bytes]


class LoginManager(OAuth2PasswordBearer):
    """
    Attributes:
        secret (starlette.datastructures.Secret): The secret used to sign and decrypt the JWT
        algorithm (str): The algorithm used to decrypt the token defaults to ``HS256``
        token_url (str): The url where the user can login to get the token
        use_cookie (bool): Whether cookies should be checked for the token
        use_header (bool): Whether headers should be checked for the token
    """

    def __init__(
        self,
        secret: Union[SECRET_TYPE, Dict[str, SECRET_TYPE]],
        token_url: str,
        algorithm="HS256",
        use_cookie=False,
        use_header=True,
        cookie_name: str = "access-token",
        custom_exception: Type[Exception] = None,
        default_expiry: timedelta = timedelta(minutes=15),
        scopes: Dict[str, str] = None,
    ):
        """
        Initializes LoginManager

        Args:
            algorithm (str): Should be "HS256" or "RS256" used to decrypt the JWT
            token_url (str): The url where the user can login to get the token
            use_cookie (bool): Set if cookies should be checked for the token
            use_header (bool): Set if headers should be checked for the token
            cookie_name (str): Name of the cookie to check for the token
            custom_exception (Exception): Exception to raise when the user is not authenticated
                this defaults to `fastapi_login.exceptions.InvalidCredentialsException`
            default_expiry (datetime.timedelta): The default expiry time of the token, defaults to 15 minutes
            scopes (Dict[str, str]): Scopes argument of OAuth2PasswordBearer for more information see
                `https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/#oauth2-security-scheme`

        """
        if use_cookie is False and use_header is False:
            raise AttributeError(
                "use_cookie and use_header are both False one of them needs to be True"
            )
        if isinstance(secret, str):
            secret = secret.encode()

        self.secret = to_secret({"algorithms": algorithm, "secret": secret})
        self._user_callback = None
        self.algorithm = algorithm

        self.tokenUrl = token_url
        self.oauth_scheme = None
        self._not_authenticated_exception = (
            custom_exception or InvalidCredentialsException
        )

        self.use_cookie = use_cookie
        self.use_header = use_header
        self.cookie_name = cookie_name
        self.default_expiry = default_expiry

        # we take over the exception raised possibly by setting auto_error to False
        super().__init__(tokenUrl=token_url, auto_error=False, scopes=scopes)

    @property
    def not_authenticated_exception(self):
        """
        Exception raised when no (valid) token is present.
        Defaults to `fastapi_login.exceptions.InvalidCredentialsException`
        The property will deprecated in the future in favor of the custom_exception argument
        on initialization
        """
        return self._not_authenticated_exception

    @not_authenticated_exception.setter
    def not_authenticated_exception(self, value: Exception):
        """
        Setter for the Exception which raises when the user is not authenticated.

        Args:
            value (Exception): The Exception you want to raise
        """
        assert issubclass(value, Exception)
        self._not_authenticated_exception = value
        warnings.warn(
            PendingDeprecationWarning(
                "Setting a custom exception this way will be deprecated in future releases. "
                "Have a look at https://fastapi-login.readthedocs.io/advanced_usage/#exception-handling"
                "for the updated way."
            )
        )

    def user_loader(self, *args, **kwargs) -> Union[Callable, Callable[..., Awaitable]]:
        """
        This sets the callback to retrieve the user.
        The function should take an unique identifier like an email
        and return the user object or None.

        Basic usage:

            >>> from fastapi import FastAPI
            >>> from fastapi_login import LoginManager

            >>> app = FastAPI()
            >>> # use import os; print(os.urandom(24).hex()) to get a suitable secret key
            >>> SECRET = "super-secret"

            >>> manager = LoginManager(SECRET, token_url="Login")

            >>> manager.user_loader()(get_user)

            >>> @manager.user_loader(...)  # Arguments and keyword arguments declared here are passed on
            >>> def get_user(user_identifier, ...):
            ...     # get user logic here

        Args:
            args: Positional arguments to pass on to the decorated method
            kwargs: Keyword arguments to pass on to the decorated method

        Returns:
            The callback
        """

        def decorator(callback: Union[Callable, Callable[..., Awaitable]]):
            """
            The actual setter of the load_user callback
            Args:
                callback (Callable or Awaitable): The callback which returns the user

            Returns:
                Partial of the callback with given args and keyword arguments already set
            """
            self._user_callback = ordered_partial(callback, *args, **kwargs)
            return callback

        # If the only argument is also a callable this will lead to errors
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # No arguments have been passed and no empty parentheses have been used
            # this was the old way (before 1.7.0) of decorating the method.
            # Thus we assume the first argument is the actual callback.
            fn = args[0]
            # If we dont empty args the callback will be passed twice to ordered_partial
            args = ()

            warnings.warn(
                SyntaxWarning(
                    "As of version 1.7.0 decorating your callback like this is not recommended anymore.\n"
                    "Please add empty parentheses like this @manager.user_loader() if you don't "
                    "wish to pass additional arguments to your callback."
                )
            )

            decorator(fn)
            return fn

        return decorator

    def _get_payload(self, token: str) -> Dict[str, typing.Any]:
        """
        Returns the decoded token payload.
        If failed, raises `LoginManager.not_authenticated_exception`

        Args:
            token (str): The token to decode

        Returns:
            Payload of the token

        Raises:
            LoginManager.not_authenticated_exception: The token is invalid or None was returned by `_load_user`
        """
        try:
            payload = jwt.decode(
                token, self.secret.secret_for_decode, algorithms=[self.algorithm]
            )
            return payload

        # This includes all errors raised by pyjwt
        except jwt.PyJWTError:
            raise self.not_authenticated_exception

    def _has_scopes(
        self, payload: Dict[str, typing.Any], required_scopes: Optional[SecurityScopes]
    ) -> bool:
        """
        Returns true if the required scopes are present in the token

        Args:
            payload (Dict[str, typing.Any]): The decoded JWT payload
            required_scopes: The scopes required to access this route

        Returns:
            True if the required scopes are contained in the tokens payload
        """
        if required_scopes is None or not required_scopes.scopes:
            # According to RFC 6749, the scopes are optional
            return True

        # when the manager was invoked using fastapi.Security(manager, scopes=[...])
        # we have to check if all required scopes are contained in the token
        provided_scopes = payload.get("scopes", [])
        # Check if enough scopes are present
        if len(provided_scopes) < len(required_scopes.scopes):
            return False
        # Check if all required scopes are present
        elif any(scope not in provided_scopes for scope in required_scopes.scopes):
            return False

        return True

    def has_scopes(self, token: str, required_scopes: SecurityScopes) -> bool:
        """
        Combines `_get_payload` and `_has_scopes` to check if the token has the required scopes

        Args:
            token (str): The token to decode
            required_scopes: The scopes required to access this route

        Returns:
            True if the required scopes are contained in the tokens payload
        """
        payload = self._get_payload(token)
        return self._has_scopes(payload, required_scopes)

    async def _get_current_user(self, payload: Dict[str, typing.Any]):
        """
        This decodes the jwt based on the secret and the algorithm set on the instance.
        If the token is correctly formatted and the user is found the user object
        is returned else this raises `LoginManager.not_authenticated_exception`

        Args:
            payload (Dict[str, typing.Any]): The decoded JWT payload

        Returns:
            The user object returned by the instances `_user_callback`

        Raises:
            LoginManager.not_authenticated_exception: The token is invalid or None was returned by `_load_user`
        """
        # the identifier should be stored under the sub (subject) key
        user_identifier = payload.get("sub")
        if user_identifier is None:
            raise self.not_authenticated_exception

        user = await self._load_user(user_identifier)
        if user is None:
            raise self.not_authenticated_exception

        return user

    async def get_current_user(self, token: str):
        """
        Combines `_get_payload` and `_get_current_user` to get the user object

        Args:
            token (str): The encoded jwt token

        Returns:
            The user object returned by the instances `_user_callback`

        Raises:
            LoginManager.not_authenticated_exception: The token is invalid or None was returned by `_load_user`
        """
        payload = self._get_payload(token)
        return await self._get_current_user(payload)

    async def _load_user(self, identifier: typing.Any):
        """
        This loads the user using the user_callback

        Args:
            identifier (Any): The user identifier expected by `_user_callback`

        Returns:
            The user object returned by `_user_callback` or None

        Raises:
            Exception: When no ``user_loader`` has been set
        """
        if self._user_callback is None:
            raise Exception("Missing user_loader callback")

        if inspect.iscoroutinefunction(self._user_callback):
            user = await self._user_callback(identifier)
        else:
            user = await run_sync(self._user_callback, identifier)

        return user

    def create_access_token(
        self, *, data: dict, expires: timedelta = None, scopes: Collection[str] = None
    ) -> str:
        """
        Helper function to create the encoded access token using
        the provided secret and the algorithm of the LoginManager instance

        Args:
            data (dict): The data which should be stored in the token
            expires (datetime.timedelta):  An optional timedelta in which the token expires.
                Defaults to 15 minutes
            scopes (Collection): Optional scopes the token user has access to.

        Returns:
            The encoded JWT with the data and the expiry. The expiry is
            available under the 'exp' key
        """

        to_encode = data.copy()

        if expires:
            expires_in = datetime.now(timezone.utc) + expires
        else:
            expires_in = datetime.now(timezone.utc) + self.default_expiry

        to_encode.update({"exp": expires_in})

        if scopes is not None:
            unique_scopes = set(scopes)
            to_encode.update({"scopes": list(unique_scopes)})

        return jwt.encode(to_encode, self.secret.secret_for_encode, self.algorithm)

    def set_cookie(self, response: Response, token: str) -> None:
        """
        Utility function to set a cookie containing token on the response

        Args:
            response (fastapi.Response): The response which is send back
            token (str): The created JWT
        """
        response.set_cookie(key=self.cookie_name, value=token, httponly=True)

    def _token_from_cookie(self, request: Request) -> typing.Optional[str]:
        """
        Checks the requests cookies for cookies with the value of`self.cookie_name` as name

        Args:
            request (fastapi.Request): The request to the route, normally filled in automatically

        Returns:
            The access token found in the cookies of the request or None
        """
        return request.cookies.get(self.cookie_name) or None

    async def _get_token(self, request: Request):
        """
        Tries to extract the token from the request, based on self.use_header and self.use_cookie

        Args:
            request: The request containing the token

        Returns:
            The in the request contained encoded JWT token

        Raises:
            LoginManager.not_authenticated_exception if no token is present
        """
        token = None
        if self.use_cookie:
            token = self._token_from_cookie(request)

        if not token and self.use_header:
            token = await super(LoginManager, self).__call__(request)

        if not token:
            raise self.not_authenticated_exception

        return token

    async def __call__(self, request: Request, security_scopes: SecurityScopes = None):
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

        token = await self._get_token(request)
        payload = self._get_payload(token)

        if not self._has_scopes(payload, security_scopes):
            raise self.not_authenticated_exception

        return await self._get_current_user(payload)

    async def optional(self, request: Request, security_scopes: SecurityScopes = None):
        """
        Acts as a dependency which catches all errors and returns `None` instead
        """
        try:
            user = await self.__call__(request, security_scopes)
        except Exception:
            return None
        else:
            return user

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
            except Exception:
                # An error occurred while getting the user
                # as middlewares are called for every incoming request
                # it's not a good idea to return the Exception
                # so we set the user to None
                request.state.user = None

            return await call_next(request)
