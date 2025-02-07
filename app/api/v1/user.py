from fastapi import APIRouter, Depends

from app.core.security import AllowRole, AuthenticatedUser
from app.models.user_model import Role
from app.schema.user_schema import UserWithId, UserWithPwd
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/", responses={400: {"description": "User already exists"}})
async def create(user: UserWithPwd, service: UserService = Depends()) -> UserWithId:
    """Create an user."""
    return await service.create(user)


@router.delete("/{id}", status_code=204, responses={404: {"description": "Not found"}})
async def delete(
    id: int,
    current_user: AuthenticatedUser,
    _: bool = Depends(AllowRole([Role.ADMIN])),
    service: UserService = Depends(),
):
    """[Admin] Delete an user."""
    await service.delete(id)


@router.get("/{id}", responses={404: {"description": "Not found"}})
async def get(id: int, current_user: AuthenticatedUser, service: UserService = Depends()) -> UserWithId:
    """Get an user data."""
    return await service.get(id)


@router.get("/")
async def get_list(
    current_user: AuthenticatedUser, service: UserService = Depends(), offset: int = 0, limit: int = 100
) -> list[UserWithId]:
    """List all users."""
    return await service.get_list(offset, limit)
