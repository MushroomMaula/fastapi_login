from typing import List
from pydantic import BaseModel

from app.models.posts import PostResponse


class UserCreate(BaseModel):
    username: str
    password: str


class UserReponse(UserCreate):

    posts: List[PostResponse]

    class Config:
        orm_mode = True
