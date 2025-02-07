from pydantic import BaseModel, EmailStr

from app.models.user_model import Role


class UserBase(BaseModel):
    name: str
    email: EmailStr

    role: Role

    class Config:
        from_attributes = True


class UserWithPwd(UserBase):
    password: str


class UserWithId(UserBase):
    id: int
