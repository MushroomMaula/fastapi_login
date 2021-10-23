from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.user import router as user_router
from app.routes.posts import router as posts_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(posts_router)
