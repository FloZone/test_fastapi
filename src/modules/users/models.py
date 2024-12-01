import enum

from pydantic import EmailStr
from sqlalchemy import Column, Enum, String
from sqlmodel import Field, SQLModel


class Role(str, enum.Enum):
    USER = 10
    ADMIN = 20


class UserBase(SQLModel):
    name: str = Field(description="User name", nullable=False)
    email: EmailStr = Field(description="User email", sa_type=String(), nullable=False, unique=True, index=True)
    role: Role = Field(description="User role", default=Role.USER, sa_column=Column(Enum(Role), nullable=False))


class UserIn(UserBase):
    password: str = Field(description="User password", nullable=False)


class UserOut(UserBase):
    id: int | None = Field(description="User ID", default=None, primary_key=True)


class UserInDb(UserOut, table=True):
    __tablename__ = "user"
    password: str = Field(nullable=False)
