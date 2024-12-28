from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username_or_email: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
