from fastapi import APIRouter, Depends

from app.core.security import AllowRole, AuthenticatedUser
from app.models.user_model import Role
from app.schema.booking_schema import BookingBase, BookingWithId
from app.services.booking_service import BookingService

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


@router.post("/", responses={400: {"description": "Value error"}, 404: {"description": "Resource not found"}})
async def create(
    booking: BookingBase, current_user: AuthenticatedUser, service: BookingService = Depends()
) -> BookingWithId:
    """Book a resource."""
    return await service.create(booking, current_user)


@router.delete(
    "/{id}", status_code=204, responses={400: {"description": "Value error"}, 404: {"description": "Not found"}}
)
async def delete(id: int, current_user: AuthenticatedUser, service: BookingService = Depends()):
    """Delete a current or future booking."""
    await service.delete(id, current_user)


@router.get("/")
async def get_list(
    current_user: AuthenticatedUser,
    service: BookingService = Depends(),
    offset: int = 0,
    limit: int = 100,
    title: str | None = None,
) -> list[BookingWithId]:
    """List user bookings."""
    return await service.get_list(offset, limit, current_user=current_user, all=False, search=title)


@router.get("/all")
async def get_list_all(
    current_user: AuthenticatedUser,
    _: bool = Depends(AllowRole([Role.ADMIN])),
    service: BookingService = Depends(),
    offset: int = 0,
    limit: int = 100,
    title: str | None = None,
) -> list[BookingWithId]:
    """[Admin] List all bookings."""
    return await service.get_list(offset, limit, current_user=current_user, all=True, search=title)


@router.get("/{id}", responses={404: {"description": "Not found"}})
async def get(id: int, current_user: AuthenticatedUser, service: BookingService = Depends()) -> BookingWithId:
    """Get a booking data."""
    return await service.get(id, current_user)


@router.put("/{id}", responses={404: {"description": "Not found"}})
async def update(
    id: int, booking: BookingBase, current_user: AuthenticatedUser, service: BookingService = Depends()
) -> BookingWithId:
    """Update a booking data only for future booking."""
    return await service.update(id, booking, current_user)
