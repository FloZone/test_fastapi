from pydantic import EmailStr
from sqlalchemy import String
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    name: str = Field(description="User name", nullable=False)
    email: EmailStr = Field(description="User email", sa_type=String(), nullable=False, unique=True, index=True)


class UserIn(UserBase):
    password: str = Field(description="User password", nullable=False)


class UserOut(UserBase):
    id: int | None = Field(description="User ID", default=None, primary_key=True)


class UserInDb(UserOut, table=True):
    __tablename__ = "user"
    password: str = Field(nullable=False)
