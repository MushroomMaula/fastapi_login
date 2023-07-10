from typing import List

from app.models.posts import PostResponse
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(UserCreate):

    posts: List[PostResponse]
    model_config = ConfigDict(from_attributes=True)
