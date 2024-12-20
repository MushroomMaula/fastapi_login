from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_login.exceptions import InvalidCredentialsException

app = FastAPI()

def query_user(email):
    return {"email": email, "password": "password"}

@app.post("/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = query_user(email)
    if not user:
        # you can return any response or error of your choice
        raise InvalidCredentialsException
    elif password != user["password"]:
        raise InvalidCredentialsException

    return {"status": "Success"}
