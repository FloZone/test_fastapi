from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from ...database import DBSession
from ...security import AllowRole, AuthenticatedUser
from ..users.models import Role
from .models import ResourceIn, ResourceInDb, ResourceOut

router = APIRouter(
    prefix="/resources",
    tags=["resources"],
)


@router.post("/", responses={400: {"description": "Resource already exists"}})
async def create(
    resource: ResourceIn, db: DBSession, current_user: AuthenticatedUser, _: bool = Depends(AllowRole([Role.ADMIN]))
) -> ResourceOut:
    """[Admin] Create a resource."""
    resource_db = ResourceInDb.model_validate(resource)
    db.add(resource_db)
    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resource already exists")
    await db.refresh(resource_db)
    return resource_db


@router.get("/")
async def list(
    db: DBSession,
    current_user: AuthenticatedUser,
    offset: int = 0,
    limit: int = 100,
    name: str | None = None,
    location: str | None = None,
) -> list[ResourceOut]:
    """List all resources."""
    statement = select(ResourceInDb)
    if name:
        statement = statement.where(ResourceInDb.name.icontains(name))
    if location:
        statement = statement.where(ResourceInDb.location.icontains(location))
    resources = (await db.execute(statement.offset(offset).limit(limit))).scalars().all()
    return resources


@router.get("/{id}", responses={404: {"description": "Not found"}})
async def get(id: int, db: DBSession, current_user: AuthenticatedUser) -> ResourceOut:
    """Get a resource data."""
    resource = await db.get(ResourceInDb, id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return resource


@router.delete("/{id}", status_code=204, responses={404: {"description": "Not found"}})
async def delete(id: int, db: DBSession, current_user: AuthenticatedUser, _: bool = Depends(AllowRole([Role.ADMIN]))):
    """[Admin] Delete a resource."""
    resource = await db.get(ResourceInDb, id)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(resource)
    await db.commit()
