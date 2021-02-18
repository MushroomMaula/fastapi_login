from fastapi.requests import Request
from fastapi.exceptions import HTTPException

def is_admin(request: Request):
    user = request.state.user
    if user is None:
        raise HTTPException(401)
    # assuming our user object has a is_admin property
    elif not user.is_admin:
        raise HTTPException(401)
    else:
        return user