from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

InvalidCredentialsException = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)