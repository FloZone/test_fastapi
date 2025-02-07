from pydantic import BaseModel, NonNegativeInt, field_validator

from app.models.resource_model import RoomType


class ResourceBase(BaseModel):
    name: str
    location: str
    capacity: NonNegativeInt
    room_type: RoomType

    class Config:
        from_attributes = True

    @field_validator("name", "location")
    @classmethod
    def name_validator(cls, value: str) -> str:
        return value.lower()


class ResourceWithId(ResourceBase):
    id: int
