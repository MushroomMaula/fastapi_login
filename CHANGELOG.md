# Changelog

## 1.10.0

- Add custom out-of-scope exception, defaults to `fastapi_login.exceptions.InsufficientScopeException`

```py
manager = LoginManager(..., out_of_scope_exception=OutOfScopeException)
```

- Remove deprecated APIs

From version 1.10.0, the following usages will be no longer available:

```py
manager.not_authenticated_exception = NotAuthenticatedException
manager = LoginManager(..., custom_exception=NotAuthenticatedException)

manager.useRequest(app)

@manager.user_loader
def load_user(email):
    ...
```

Use these instead:

```py
manager = LoginManager(..., not_authenticated_exception=NotAuthenticatedException)

manager.attach_middleware(app)

@manager.user_loader()
def load_user(email):
    ...
```

## 1.9.3

- Refactor decoding token
- Remove `passlib`
- Bump dependencies

Now `passlib` should be used directly. This may be a breaking change for some users.

```py
from config import DEFAULT_SETTINGS
from passlib.context import CryptContext

from fastapi_login import LoginManager

manager = LoginManager(DEFAULT_SETTINGS.secret, DEFAULT_SETTINGS.token_url)
pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(plaintext_password: str):
    """Return the hash of a password"""
    return pwd_context.hash(plaintext_password)


def verify_password(password_input: str, hashed_password: str):
    """Check if the provided password matches"""
    return pwd_context.verify(password_input, hashed_password)
```

## 1.9.2

- Revamp compatibility with `Pydantic`
- Bump dependencies

## 1.9.1

Mostly fixes and updates in regard to `Pydantic` v2. Thanks to [kigawas](https://github.com/kigawas).

- Update examples to support `Pydantic` v2.
- Fix potential type error against `Pydantic` v2.
- Add example dependencies in `pyproject.toml`.
- Remove `setup.py`
- Fixed example (Thanks [Lexachoc](https://github.com/Lexachoc))
- Fixed return type of user_loader (Thanks [kazunorimiura](https://github.com/kazunorimiura))

## 1.9.0

- User callback is now run asynchronous without blocking the worker thread [#92](https://github.com/MushroomMaula/fastapi_login/pull/97)
- ``custom_exception`` argument has now correct type [#97](https://github.com/MushroomMaula/fastapi_login/pull/97)
- Fixed some minor security issues by updating packages
- Now includes ``LoginManager.optional`` which will return `None` instead of raising an exception.
  An [example](https://fastapi-login.readthedocs.io/usage/#returning-none-instead-of-raising-an-exception) has been added to the documentation.

## 1.8.3

- Pin pyjwt dependency (Fixes [#94](https://github.com/MushroomMaula/fastapi_login/issues/94))
- Switched from `setup.py` based publishing to using `pyproject.toml` together with poetry
- Switched publishing to poetry
- Update requirements in the examples projects
- Added correct header in `/examples/simples/templates/index.html` (Fixes [#93](https://github.com/MushroomMaula/fastapi_login/issues/93) and [#95](https://github.com/MushroomMaula/fastapi_login/issues/95))

## 1.8.2

Update pyjwt to version 2.4.0, to fix a security issue in version 2.1.0

## 1.8.1

Fixes [#78](https://github.com/MushroomMaula/fastapi_login/issues/78)

## 1.8.0

- Adds support for asymmetric key algorithms thanks to [filwaline](https://github.com/filwaline).
Documentation for this feature can be found
[here](https://fastapi-login.readthedocs.io/advanced_usage/#asymmetric-algorithms).

- Fixes syntax of ``__all__`` inside `fastapi_login/__init__.py`. (Thanks to [kigawas](https://github.com/kigawas))
- Fixes multiple issues in the documentation. (Thanks to [alwye](https://github.com/alwye))
- Bumps version of ``mkdocs`` to fix a security issue. As this is a dev dependency it shouldn't have affected any user.

## 1.7.3

Fixes not being able to import LoginManager in Python versions < 3.8. ([#61](https://github.com/MushroomMaula/fastapi_login/issues/61))

Fixes bug not authenticating user when more than the required scopes are present ([#63](https://github.com/MushroomMaula/fastapi_login/issues/63))

Adds a new example project (work still in progress).

## 1.7.2

Fixes not being able to call your decorated function on its own anymore.
This was caused because the decorator did not return the function.

## 1.7.1

Fixes backwards compatibility ([#58](https://github.com/MushroomMaula/fastapi_login/issues/58)) of the ``LoginManager.user_loader`` decorator.

In version 1.7.0 it was not possible to do the following anymore:

```py
@manager.user_loader
def load_user(email):
    ...
```

This has been fixed now.

It is however recommended to just add empty parentheses after the decorator
if you don't wish to pass extra arguments to your callback.

```python
@manager.user_loader()
def load_user(email):
    ...
```

Because of the backwards compatibility it is not possible to pass a
callable object as the first argument to the decorator.
If this is needed it has to be passed as a keyword argument.
This is detailed more in depth in the [documentation](https://fastapi-login.readthedocs.io/advanced_usage/#predefining-additional-user_loader-arguments).

## 1.7.0

Configuration is now more pythonic using arguments on initialization
    instead of class attributes

- The recommended way of setting custom exceptions is now using
    the ``custom_exception`` argument on initialization. Thanks to [kigawas](https://github.com/kigawas) for the idea.
- The default token expiry can now be changed on initialization using the ``default_expiry`` argument
- The cookie name can now be changed on initialization using the ``cookie_name`` argument.

Added ``py.typed`` file for better mypy support.

The ``user_loader`` decorator now takes (keyword) arguments, which will then be used, when
the declared callback is called. Have a look at the [documentation](https://fastapi-login.readthedocs.io/advanced_usage/#predefining-additional-user_loader-arguments)

## 1.6.3

- Fixes bug not being able to catch ``LoginManager.not_authenticated_exception`` in ``LoginManager.has_scopes``. ([#47](https://github.com/MushroomMaula/fastapi_login/issues/47) thanks to [kigawas](https://github.com/kigawas))

## 1.6.2

- Adds support for OAuth2 scopes.

    If used with ``fastapi.Security`` instead of ``fastapi.Depends``, token are now
    check for the required scopes to access the route.
    For more checkout the [documentation](https://fastapi-login.readthedocs.io/advanced_usage/#oauth2-scopes)

## 1.6.1

- Updates of dependencies, this fixes several security issues found in the dependencies

## 1.6.0

- Renamed the ``tokenUrl`` argument to ``token_url``
- User set `LoginManager.not_authenticated_exception`` will now also be raised when a token expires,
   or the token has an invalid format. (Fixes [#28](https://github.com/MushroomMaula/fastapi_login/issues/28))
- Examples have been [added](https://github.com/MushroomMaula/fastapi_login/tree/master/examples) showing how to use ``fastapi-login``
- Rewrote most of the tests
- Update packages to fix security vulnerability
- Update README to reflect package changes

## 1.5.3

- Vastly improve documentation
- Add middleware support [#24](https://github.com/MushroomMaula/fastapi_login/pull/24) (thanks to [zarlo](https://github.com/zarlo))

## 1.5.2

- Update packages to its latest stable version
- Fix error trying to decode the token, which is a string in newer versions of pyjwt [#21](https://github.com/MushroomMaula/fastapi_login/issues/21)
- Fixed a typo in the changelog

## 1.5.1

- Improve cookie support, now allows headers and cookies to be used at the same time.
- Stops assuming every cookie is prefixed with ``Bearer``
- Improved testing coverage and docs

## 1.5.0

- Add cookie support

## 1.4.0

- Fix security vulnerability found in uvicorn

## 1.3.0

Added OpenAPI support

## 1.2.2

- Removed the provided config object and improved docstrings

## 1.1.0

- Remove the need for a config on the app instance. You now have to provide
 the secret key on Initiation.
