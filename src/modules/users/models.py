from pydantic import EmailStr
from sqlalchemy import String
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    name: str = Field(nullable=False)
    email: EmailStr = Field(sa_type=String(), nullable=False, unique=True, index=True)


class UserIn(UserBase):
    password: str = Field(nullable=False)


class UserOut(UserBase):
    id: int | None = Field(default=None, primary_key=True)


class UserInDb(UserOut, table=True):
    __tablename__ = "user"
    password: str = Field(nullable=False)
