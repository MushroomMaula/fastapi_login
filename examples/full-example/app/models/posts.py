import datetime
from pydantic import BaseModel


class PostCreate(BaseModel):
    text: str


class PostResponse(PostCreate):

    created_at: datetime.datetime

    class Config:
        orm_mode = True
