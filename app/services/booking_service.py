from datetime import datetime

from fastapi import Depends

from app.core.exceptions import NotAvailableException, NotFoundException, ValidationException
from app.models.user_model import Role
from app.repositories.booking_repository import BookingRepository
from app.repositories.resource_repository import ResourceRepository
from app.schema.booking_schema import BookingBase, BookingWithId, BookingWithOwner
from app.schema.user_schema import UserWithId
from app.services.service import AbstractService


class BookingService(AbstractService):
    def __init__(
        self, booking_repository: BookingRepository = Depends(), resource_repository: ResourceRepository = Depends()
    ):
        self.booking_repository = booking_repository
        self.resource_repository = resource_repository

    async def create(self, booking: BookingBase, current_user: UserWithId = None) -> BookingWithId:
        booking = BookingWithOwner(**booking.model_dump(), owner_id=current_user.id)
        # Check if resource is available
        if not await self.is_resource_available(booking.resource_id, booking.start, booking.end):
            raise NotAvailableException()
        return await self.booking_repository.create(booking)

    async def delete(self, id: int, current_user: UserWithId = None):
        booking = await self.booking_repository.get(id)
        # If user is not admin and try to access a booking that is not his own
        if current_user.role.value < Role.ADMIN.value and booking.owner_id != current_user.id:
            raise NotFoundException()
        # Cannot delete past bookings
        if booking.end.astimezone() <= datetime.now().astimezone():
            raise ValidationException()
        await self.booking_repository.delete(id)

    async def get(self, id: int, current_user: UserWithId = None) -> BookingWithId:
        booking = await self.booking_repository.get(id)
        # If user is not admin and try to access a booking that is not his own
        if current_user.role.value < Role.ADMIN.value and booking.owner_id != current_user.id:
            raise NotFoundException()
        return booking

    async def get_list(
        self, offset: int, limit: int, current_user: UserWithId = None, all: bool = False, search: str = None
    ) -> list[BookingWithId]:
        return await self.booking_repository.get_list(offset, limit, current_user.id, all, search)

    async def update(self, id: int, booking: BookingBase, current_user: UserWithId = None) -> BookingWithId:
        booking_db = await self.booking_repository.get(id)
        # If user is not admin and try to access a booking that is not his own
        if current_user.role.value < Role.ADMIN.value and booking_db.owner_id != current_user.id:
            raise NotFoundException()
        # Can update future booking but not current or past ones
        if booking_db.end.astimezone() < datetime.now().astimezone():
            raise ValidationException()
        # Check if resource is available: get all bookings in the given slot except the current one
        bookings = await self.booking_repository.get_resource_bookings_in_slot(
            booking.resource_id, booking.start, booking.end
        )
        if id in [b.id for b in bookings] and len(bookings) > 1:
            raise NotAvailableException()

        booking_data = BookingWithOwner(**booking.model_dump(), owner_id=current_user.id)
        return await self.booking_repository.update(id, booking_data)

    async def is_resource_available(self, id: int, start: datetime, end: datetime) -> bool:
        bookings = await self.booking_repository.get_resource_bookings_in_slot(id, start, end)
        return False if bookings else True
