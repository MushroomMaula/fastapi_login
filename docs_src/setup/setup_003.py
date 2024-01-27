from fastapi import FastAPI

from fastapi_login import LoginManager

app = FastAPI()

SECRET = "super-secret-key"
manager = LoginManager(SECRET, "/login")
