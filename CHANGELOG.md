#1.6.1
- Updates of dependencies, this fixes several security issues found in the dependencies

#1.6.0
- Renamed the ``tokenUrl`` argument to ``token_url``
 - User set `LoginManager.not_authenticated_exception`` will now also be raised when a token expires, 
   or the token has an invalid format. (Fixes [#28](https://github.com/MushroomMaula/fastapi_login/issues/28))
- Examples have been [added](https://github.com/MushroomMaula/fastapi_login/tree/master/examples) showing how to use ``fastapi-login``
- Rewrote most of the tests
- Update packages to fix security vulnerability
- Update README to reflect package changes


#1.5.3
- Vastly improve documentation
- Add middleware support [#24](https://github.com/MushroomMaula/fastapi_login/pull/24) (thanks to [zarlo](https://github.com/zarlo))

#1.5.2
- Update packages to its latest stable version
- Fix error trying to decode the token, which is a string in newer versions of pyjwt [#21](https://github.com/MushroomMaula/fastapi_login/issues/21)
- Fixed a typo in the changelog

#1.5.1
- Improve cookie support, now allows headers and cookies to be used at the same time.
- Stops assuming every cookie is prefixed with ``Bearer``
- Improved testing coverage and docs

#1.5.0
- Add cookie support

#1.4.0
- Fix security vulnerability found in uvicorn

#1.3.0
Added OpenAPI support

#1.2.2
- Removed the provided config object and improved docstrings

# 1.1.0
- Remove the need for a config on the app instance. You now have to provide
 the secret key on Initiation.