from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import select

from app.core.database import DBSession
from app.core.exceptions import DuplicateException, NotFoundException, ValidationException
from app.models.resource_model import ResourceInDb
from app.schema.resource_schema import ResourceBase, ResourceWithId


class ResourceRepository:
    def __init__(self, db: DBSession):
        self.db = db

    async def create(self, resource: ResourceBase) -> ResourceWithId:
        try:
            resource_db = ResourceInDb.model_validate(resource)
        except ValidationError:
            raise ValidationException()
        self.db.add(resource_db)
        try:
            await self.db.commit()
        except IntegrityError:
            raise DuplicateException()
        await self.db.refresh(resource_db)
        return resource_db

    async def delete(self, id: int):
        resource_db = await self.db.get(ResourceInDb, id)
        if not resource_db:
            raise NotFoundException()
        try:
            await self.db.delete(resource_db)
        except SQLAlchemyError:
            raise NotFoundException()
        await self.db.commit()

    async def get(self, id: int) -> ResourceWithId:
        resource_db = await self.db.get(ResourceInDb, id)
        if not resource_db:
            raise NotFoundException()
        return resource_db

    async def get_list(self, offset: int, limit: int, name: str, location: str) -> list[ResourceWithId]:
        query = select(ResourceInDb)
        if name:
            query = query.where(ResourceInDb.name.icontains(name))
        if location:
            query = query.where(ResourceInDb.location.icontains(location))
        return (await self.db.execute(query.offset(offset).limit(limit))).scalars().all()

    async def update(self, id: int, resource: ResourceBase) -> ResourceWithId:
        resource_db = await self.db.get(ResourceInDb, id)
        if not resource_db:
            raise NotFoundException()
        for key, value in resource.model_dump().items():
            setattr(resource_db, key, value)
        try:
            await self.db.commit()
        except IntegrityError:
            raise ValidationException()
        await self.db.refresh(resource_db)
        return resource_db
