import enum

from pydantic import EmailStr
from sqlalchemy import Column, Enum, String
from sqlmodel import Field, Relationship, SQLModel


class Role(str, enum.Enum):
    USER = 10
    ADMIN = 20


class UserInDb(SQLModel, table=True):
    __tablename__ = "user"
    id: int = Field(description="User ID", default=None, primary_key=True)
    name: str = Field(description="User name", nullable=False)
    email: EmailStr = Field(description="User email", sa_type=String(), nullable=False, unique=True, index=True)
    role: Role = Field(description="User role", default=Role.USER, sa_column=Column(Enum(Role), nullable=False))
    password: str = Field(nullable=False)

    bookings: list["BookingInDb"] = Relationship(back_populates="owner", cascade_delete=True)  # type: ignore  # noqa
