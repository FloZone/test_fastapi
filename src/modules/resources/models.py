import enum
from datetime import datetime
from enum import auto

from pydantic import NonNegativeInt, field_validator
from sqlalchemy import CheckConstraint, Column, Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, Relationship, SQLModel, and_, or_, select


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

    bookings: list["BookingInDb"] = Relationship(back_populates="resource", cascade_delete=True)  # type: ignore  # noqa

    @field_validator("name", "location")
    @classmethod
    def name_validator(cls, value: str) -> str:
        return value.lower()

    @classmethod
    async def is_available(
        cls, db: AsyncSession, resource_id: int, start: datetime, end: datetime, current_booking_id: int = None
    ) -> bool:
        """Return whether the resource is available on the given dates excluding the current booking if provided."""
        from ..bookings.models import BookingInDb

        # Search bookings scheduled during the start or the end date
        statement = (
            select(BookingInDb)
            .where(BookingInDb.id != current_booking_id)
            .where(BookingInDb.resource_id == resource_id)
            .where(
                or_(
                    and_(BookingInDb.start <= start, start < BookingInDb.end),
                    and_(BookingInDb.start < end, end <= BookingInDb.end),
                )
            )
        )
        existing_bookings = (await db.execute(statement)).scalars().all()
        return False if existing_bookings else True
