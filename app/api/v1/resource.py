from fastapi import APIRouter, Depends

from app.core.security import AllowRole, AuthenticatedUser
from app.models.user_model import Role
from app.schema.resource_schema import ResourceBase, ResourceWithId
from app.services.resource_service import ResourceService

router = APIRouter(
    prefix="/resources",
    tags=["resources"],
)


@router.post("/", responses={400: {"description": "Resource already exists"}})
async def create(
    resource: ResourceBase,
    current_user: AuthenticatedUser,
    _: bool = Depends(AllowRole([Role.ADMIN])),
    service: ResourceService = Depends(),
) -> ResourceWithId:
    """[Admin] Create a resource."""
    return await service.create(resource)


@router.delete("/{id}", status_code=204, responses={404: {"description": "Not found"}})
async def delete(
    id: int,
    current_user: AuthenticatedUser,
    _: bool = Depends(AllowRole([Role.ADMIN])),
    service: ResourceService = Depends(),
):
    """[Admin] Delete a resource."""
    await service.delete(id)


@router.get("/{id}", responses={404: {"description": "Not found"}})
async def get(id: int, current_user: AuthenticatedUser, service: ResourceService = Depends()) -> ResourceWithId:
    """Get a resource data."""
    return await service.get(id)


@router.get("/")
async def get_list(
    current_user: AuthenticatedUser,
    service: ResourceService = Depends(),
    offset: int = 0,
    limit: int = 100,
    name: str | None = None,
    location: str | None = None,
) -> list[ResourceWithId]:
    """List all resources."""
    return await service.get_list(offset, limit, name, location)
