# About

**Source Code: [https://github.com/MushroomMaula/fastapi_login](https://github.com/MushroomMaula/fastapi_login)**

`fastapi-login` provides a convenient, simple to use user authentication for FastAPI.

## Features

- Provides a simple authorization dependency
- Support for token in either request headers or as cookie
- Usable as a middleware to create your own dependencies
- Support for callbacks when user is unauthorized
- Support for OAuth2 scopes
- OpenAPI support

## Aim

The idea of ``fastapi-login`` is to provide an easy to use and setup authorization system for your routes
while being as barebone and customizable as possible. Therefore, no default database user model or
login/registration routes are provided in the packages.

If thats what you need there are other packages which provide more functionality out of the box such as
[fastapi-users](https://github.com/frankie567/fastapi-users).
