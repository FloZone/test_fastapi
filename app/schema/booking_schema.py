from datetime import datetime

from pydantic import BaseModel


class BookingBase(BaseModel):
    title: str
    start: datetime
    end: datetime
    resource_id: int

    class Config:
        from_attributes = True


class BookingWithOwner(BookingBase):
    owner_id: int


class BookingWithId(BookingWithOwner):
    id: int
