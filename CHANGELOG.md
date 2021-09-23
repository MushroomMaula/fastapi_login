# 1.7.1
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
````python
@manager.user_loader()
def load_user(email):
    ...
````
Because of the backwards compatibility it is not possible to pass a 
callable object as the first argument to the decorator.
If this is needed it has to be passed as a keyword argument.
This is detailed more in depth in the [documentation](https://fastapi-login.readthedocs.io/advanced_usage/#predefining-additional-user_loader-arguments).

# 1.7.0
Configuration is now more pythonic using arguments on initialization
    instead of class attributes
- The recommended way of setting custom exceptions is now using
    the ``custom_exception`` argument on initialization. Thanks to [kigawas](https://github.com/kigawas) for the idea.
- The default token expiry can now be changed on initialization using the ``default_expiry`` argument
- The cookie name can now be changed on initialization using the ``cookie_name`` argument.

Added ``py.typed`` file for better mypy support.

The ``user_loader`` decorator now takes (keyword) arguments, which will then be used, when
the declared callback is called. Have a look at the [documentation](https://fastapi-login.readthedocs.io/advanced_usage/#predefining-additional-user_loader-arguments)

# 1.6.3
- Fixes bug not being able to catch ``LoginManager.not_authenticated_exception`` in ``LoginManager.has_scopes``. ([#47](https://github.com/MushroomMaula/fastapi_login/issues/47) thanks to [kigawas](https://github.com/kigawas))

# 1.6.2
- Adds support for OAuth2 scopes.
  
    If used with ``fastapi.Security`` instead of ``fastapi.Depends``, token are now
    check for the required scopes to access the route.
    For more checkout the [documentation](https://fastapi-login.readthedocs.io/advanced_usage/#oauth2-scopes) 

# 1.6.1
- Updates of dependencies, this fixes several security issues found in the dependencies

# 1.6.0
- Renamed the ``tokenUrl`` argument to ``token_url``
 - User set `LoginManager.not_authenticated_exception`` will now also be raised when a token expires, 
   or the token has an invalid format. (Fixes [#28](https://github.com/MushroomMaula/fastapi_login/issues/28))
- Examples have been [added](https://github.com/MushroomMaula/fastapi_login/tree/master/examples) showing how to use ``fastapi-login``
- Rewrote most of the tests
- Update packages to fix security vulnerability
- Update README to reflect package changes


# 1.5.3
- Vastly improve documentation
- Add middleware support [#24](https://github.com/MushroomMaula/fastapi_login/pull/24) (thanks to [zarlo](https://github.com/zarlo))

# 1.5.2
- Update packages to its latest stable version
- Fix error trying to decode the token, which is a string in newer versions of pyjwt [#21](https://github.com/MushroomMaula/fastapi_login/issues/21)
- Fixed a typo in the changelog

# 1.5.1
- Improve cookie support, now allows headers and cookies to be used at the same time.
- Stops assuming every cookie is prefixed with ``Bearer``
- Improved testing coverage and docs

# 1.5.0
- Add cookie support

# 1.4.0
- Fix security vulnerability found in uvicorn

# 1.3.0
Added OpenAPI support

# 1.2.2
- Removed the provided config object and improved docstrings

# 1.1.0
- Remove the need for a config on the app instance. You now have to provide
 the secret key on Initiation.