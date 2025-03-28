from fastapi import Depends

from app.repositories.user_repository import UserRepository
from app.schema.user_schema import UserWithId, UserWithPwd
from app.services.service import AbstractService


class UserService(AbstractService):
    def __init__(self, user_repository: UserRepository = Depends()):
        self.user_repository = user_repository

    async def create(self, user: UserWithPwd) -> UserWithId:
        from app.core.security import hash_password

        user.password = hash_password(user.password)
        return await self.user_repository.create(user)

    async def delete(self, id: int):
        await self.user_repository.delete(id)

    async def get(self, id: int) -> UserWithId:
        return await self.user_repository.get(id)

    async def get_with_username(self, username: str) -> UserWithId:
        return await self.user_repository.get_with_username(username)

    async def get_list(self, offset: int, limit: int) -> list[UserWithId]:
        return await self.user_repository.get_list(offset, limit)

    def update(self, id: int, object):
        """We don't allow user modification."""
        pass
