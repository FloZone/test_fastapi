from fastapi import Depends

from app.repositories.user_repository import UserRepository
from app.schema.user_schema import UserWithId, UserWithPwd


# TODO crééer une interface BaseService et BaseRepository
class UserService:
    def __init__(self, user_repository: UserRepository = Depends()):
        self.user_repository = user_repository

    async def create(self, user: UserWithPwd) -> UserWithId:
        # TODO remettre ça en haut, se débrouiller pour ne plus avoir d'import circulaire
        from app.core.security import hash_password

        user.password = hash_password(user.password)
        return await self.user_repository.create(user)

    async def delete(self, id: int):
        await self.user_repository.delete(id)

    async def get(self, id: int) -> UserWithId:
        return await self.user_repository.get(id)

    async def get_list(self, offset: int, limit: int) -> list[UserWithId]:
        return await self.user_repository.get_list(offset, limit)
