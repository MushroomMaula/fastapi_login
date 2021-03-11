import uuid

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from pydantic import BaseModel, UUID4

from config import DEFAULT_SETTINGS
from crud_models import UserCreate, UserResponse
from db import get_db, Base, engine
from db_actions import get_user, create_user
from security import manager, verify_password


app = FastAPI()


@app.on_event("startup")
def setup():
    print("Creating db tables...")
    Base.metadata.create_all(bind=engine)
    print(f"Created {len(engine.table_names())} tables: {engine.table_names()}")

@app.post("/auth/register")
def register(user: UserCreate, db=Depends(get_db)):
    if get_user(user.email) is not None:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    else:
        db_user = create_user(db, user)
        return UserResponse(id=db_user.id, email=db_user.email, is_admin=db_user.is_admin)


@app.post(DEFAULT_SETTINGS.token_url)
def login(data: OAuth2PasswordRequestForm = Depends()):
    email = data.username
    password = data.password

    user = get_user(email)  # we are using the same function to retrieve the user
    if user is None:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif not verify_password(password, user.password):
        raise InvalidCredentialsException
    
    access_token = manager.create_access_token(
        data=dict(sub=user.email)
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}


@app.get("/private")
def private_route(user=Depends(manager)):
    return {"detail": f"Welcome {user.email}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app")