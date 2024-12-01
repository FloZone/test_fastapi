import enum
from enum import auto

from pydantic import NonNegativeInt, field_validator
from sqlalchemy import CheckConstraint, Column, Enum
from sqlmodel import Field, SQLModel


class RoomType(enum.StrEnum):
    AUDITORIUM = auto()
    BOX = auto()
    CONFERENCE_ROOM = auto()
    DESK = auto()
    MEETING_ROOM = auto()
    OPEN_SPACE = auto()


class ResourceBase(SQLModel):
    name: str = Field(description="Resource name", nullable=False, unique=True, index=True)
    location: str | None = Field(description="Resource location", nullable=True)
    capacity: NonNegativeInt = Field(
        description="Resource capacity", default=0, nullable=False, sa_column_args=[CheckConstraint("capacity>=0")]
    )
    room_type: RoomType = Field(
        description="Resource type", default=RoomType.AUDITORIUM, sa_column=Column(Enum(RoomType), nullable=False)
    )


class ResourceIn(ResourceBase):
    pass


class ResourceOut(ResourceBase):
    id: int | None = Field(description="Resource ID", default=None, primary_key=True)


class ResourceInDb(ResourceOut, table=True):
    __tablename__ = "resource"

    @field_validator("name", "location")
    @classmethod
    def name_validator(cls, value: str) -> str:
        return value.lower()
