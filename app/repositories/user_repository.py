from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import select

from app.core.database import DBSession
from app.core.exceptions import DuplicateException, NotFoundException, ValidationException
from app.models.user_model import UserInDb
from app.repositories.repository import AbstractRepository
from app.schema.user_schema import UserWithId, UserWithPwd


class UserRepository(AbstractRepository):
    def __init__(self, db: DBSession):
        self.db = db

    async def create(self, user: UserWithPwd) -> UserWithId:
        try:
            user_db = UserInDb.model_validate(user)
        except ValidationError:
            raise ValidationException()
        self.db.add(user_db)
        try:
            await self.db.commit()
        except IntegrityError:
            raise DuplicateException()
        await self.db.refresh(user_db)
        return user_db

    async def delete(self, id: int):
        user_db = await self.db.get(UserInDb, id)
        if not user_db:
            raise NotFoundException()
        try:
            await self.db.delete(user_db)
        except SQLAlchemyError:
            raise NotFoundException()
        await self.db.commit()

    async def get(self, id: int) -> UserWithId:
        user_db = await self.db.get(UserInDb, id)
        if not user_db:
            raise NotFoundException()
        return user_db

    async def get_with_username(self, username: str) -> UserWithId:
        user_db = (await self.db.execute(select(UserInDb).where(UserInDb.email == username))).scalars().first()
        if not user_db:
            raise NotFoundException()
        return user_db

    async def get_list(self, offset: int, limit: int) -> list[UserWithId]:
        return (await self.db.execute(select(UserInDb).offset(offset).limit(limit))).scalars().all()

    def update(self, id: int, object):
        """We don't allow user modification."""
        pass
