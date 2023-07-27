import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import UUID4, BaseModel, ConfigDict
from pydantic_settings import BaseSettings

from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException


class Settings(BaseSettings):
    secret: str = "" # automatically taken from environment variable


class UserCreate(BaseModel):
    email: str
    password: str
    model_config = ConfigDict(from_attributes=True)



class User(UserCreate):
    id: UUID4


DEFAULT_SETTINGS = Settings(_env_file=".env")
DB = {
    "users": {}
}
TOKEN_URL = "/auth/token"

app = FastAPI()
manager = LoginManager(DEFAULT_SETTINGS.secret, TOKEN_URL)


@manager.user_loader()
def get_user(email: str):
    return DB["users"].get(email)


@app.get("/")
def index():
    with open("./templates/index.html", 'r') as f:
        return HTMLResponse(content=f.read())


@app.post("/auth/register")
def register(user: UserCreate):
    if user.email in DB["users"]:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    else:
        db_user = User(**user.dict(), id=uuid.uuid4())
        # PLEASE hash your passwords in real world applications
        DB["users"][db_user.email] = db_user
        return {"detail": "Successful registered"}


@app.post(TOKEN_URL)
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = get_user(email)  # we are using the same function to retrieve the user
    if not user:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif password != user.password:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=email)
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get("/private")
def private_route(user=Depends(manager)):
    return {"detail": f"Welcome {user.email}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app")
