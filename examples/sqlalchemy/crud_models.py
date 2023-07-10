from pydantic import ConfigDict, BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    is_admin: bool
    model_config = ConfigDict(from_attributes=True)
