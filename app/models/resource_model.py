import enum
from enum import auto

from sqlalchemy import CheckConstraint, Column, Enum
from sqlmodel import Field, Relationship, SQLModel


class RoomType(enum.StrEnum):
    AUDITORIUM = auto()
    BOX = auto()
    CONFERENCE_ROOM = auto()
    DESK = auto()
    MEETING_ROOM = auto()
    OPEN_SPACE = auto()


class ResourceInDb(SQLModel, table=True):
    __tablename__ = "resource"
    id: int | None = Field(description="Resource ID", default=None, primary_key=True)
    name: str = Field(description="Resource name", nullable=False, unique=True, index=True)
    location: str | None = Field(description="Resource location", nullable=True)
    capacity: int = Field(
        description="Resource capacity", default=0, nullable=False, sa_column_args=[CheckConstraint("capacity>=0")]
    )
    room_type: RoomType = Field(
        description="Resource type", default=RoomType.AUDITORIUM, sa_column=Column(Enum(RoomType), nullable=False)
    )
    bookings: list["BookingInDb"] = Relationship(back_populates="resource", cascade_delete=True)  # type: ignore  # noqa
