from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

# Reference: https://datatracker.ietf.org/doc/html/rfc6749#section-5.2

InvalidCredentialsException = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

InsufficientScopeException = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="Insufficient scope",
    headers={"WWW-Authenticate": "Bearer"},
)
