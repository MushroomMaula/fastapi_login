#1.5.1
- Improve cookie support, now allows headers and cookies to be used at the same time.
- Stops assuming every cookie is prefixed with ``Bearer``
- Improved testing coverage and docs

#1.5.0
- Add cookie support

#1.4.0
- Fix security vulnerability found in uvicorn

#1.3.0
A- dded OpenAPI support

#1.2.2
- Removed the provided config object and improved docstrings

# 1.1.0
- Remove the need for a config on the app instance. You now have to provide
 the secret key on Initiation.