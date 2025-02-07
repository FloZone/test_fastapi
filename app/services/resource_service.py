from fastapi import Depends

from app.repositories.booking_repository import BookingRepository
from app.repositories.resource_repository import ResourceRepository
from app.schema.resource_schema import ResourceBase, ResourceWithId


class ResourceService:
    def __init__(
        self, resource_repository: ResourceRepository = Depends(), booking_repository: BookingRepository = Depends()
    ):
        self.resource_repository = resource_repository
        self.booking_repository = booking_repository

    async def create(self, resource: ResourceBase) -> ResourceWithId:
        return await self.resource_repository.create(resource)

    async def delete(self, id: int):
        await self.resource_repository.delete(id)

    async def get(self, id: int) -> ResourceWithId:
        return await self.resource_repository.get(id)

    async def get_list(self, offset: int, limit: int, name: str = None, location: str = None) -> list[ResourceWithId]:
        return await self.resource_repository.get_list(offset, limit, name, location)

    async def update(self, id: int, resource: ResourceBase) -> ResourceWithId:
        return await self.resource_repository.update(id, resource)
