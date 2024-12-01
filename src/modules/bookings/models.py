from pydantic import FutureDatetime, ValidationInfo, field_validator
from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

from ...modules.resources.models import ResourceInDb
from ...modules.users.models import UserInDb


class BookingBase(SQLModel):
    title: str = Field(description="Booking subject", nullable=False)
    start: FutureDatetime = Field(
        description="Booking start date & time", sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    end: FutureDatetime = Field(
        description="Booking end date & time", sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class BookingIn(BookingBase):
    resource_id: int = Field(description="Resource ID to book", nullable=False)


class BookingOut(BookingBase):
    id: int = Field(description="Booking ID", nullable=False)
    resource_id: int = Field(description="Booked resource ID", nullable=False)


class BookingInDb(BookingBase, table=True):
    __tablename__ = "booking"
    id: int | None = Field(description="Resource ID", default=None, primary_key=True)

    owner_id: int = Field(nullable=False, foreign_key="user.id")
    owner: UserInDb = Relationship(back_populates="bookings")

    resource_id: int = Field(nullable=False, foreign_key="resource.id")
    resource: ResourceInDb = Relationship(back_populates="bookings")

    @field_validator("end")
    @classmethod
    def end_date_validator(cls, value: FutureDatetime, info: ValidationInfo) -> FutureDatetime:
        """Check that end datetime is after start datetime."""
        if value <= info.data["start"]:
            raise ValueError(f"'{info.field_name}' must be after the booking start date time")
        return value
