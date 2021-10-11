import datetime
from pydantic import BaseModel


class PostCreate(BaseModel):
    text: str


class PostResponse(PostCreate):

    create_at: datetime.datetime

    class Config:
        from_orm = True
