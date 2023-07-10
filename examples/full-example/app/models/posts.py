import datetime
from pydantic import ConfigDict, BaseModel


class PostCreate(BaseModel):
    text: str


class PostResponse(PostCreate):

    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)
