from fastapi import Request
from starlette.responses import RedirectResponse


class NotAuthenticatedException(Exception):
    pass

# Before version 1.7.0
# manager.not_authenticated_exception = NotAuthenticatedException

# The updated way
manager = LoginManager(
    ...,
    custom_exception=NotAuthenticatedException
)

@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url='/login')

