from datetime import datetime

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import and_, or_, select

from app.core.database import DBSession
from app.core.exceptions import DuplicateException, NotFoundException, ValidationException
from app.models.booking_model import BookingInDb
from app.repositories.repository import AbstractRepository
from app.schema.booking_schema import BookingWithId, BookingWithOwner


class BookingRepository(AbstractRepository):
    def __init__(self, db: DBSession):
        self.db = db

    async def create(self, booking: BookingWithOwner) -> BookingWithId:
        try:
            booking_db = BookingInDb.model_validate(booking)
        except ValidationError:
            raise ValidationException()
        self.db.add(booking_db)
        try:
            await self.db.commit()
        except IntegrityError:
            raise DuplicateException()
        await self.db.refresh(booking_db)
        return booking_db

    async def delete(self, id: int):
        booking_db = await self.db.get(BookingInDb, id)
        if not booking_db:
            raise NotFoundException()
        try:
            await self.db.delete(booking_db)
        except SQLAlchemyError:
            raise NotFoundException()
        await self.db.commit()

    async def get(self, id: int) -> BookingWithId:
        booking_db = await self.db.get(BookingInDb, id)
        if not booking_db:
            raise NotFoundException()
        return booking_db

    async def get_list(
        self, offset: int, limit: int, owner_id: int = None, all: bool = False, search: str = None
    ) -> list[BookingWithId]:
        query = select(BookingInDb)
        if not all:
            query = query.where(BookingInDb.owner_id == owner_id)
        if search:
            query = query.where(BookingInDb.title.icontains(search))
        return (await self.db.execute(query.offset(offset).limit(limit))).scalars().all()

    async def update(self, id: int, booking: BookingWithOwner) -> BookingWithId:
        booking_db = await self.db.get(BookingInDb, id)
        if not booking_db:
            raise NotFoundException()
        for key, value in booking.model_dump().items():
            setattr(booking_db, key, value)
        try:
            await self.db.commit()
        except IntegrityError:
            raise ValidationException()
        await self.db.refresh(booking_db)
        return booking_db

    async def get_resource_bookings_in_slot(
        self, resource_id: int, start: datetime, end: datetime
    ) -> list[BookingWithId]:
        query = (
            select(BookingInDb)
            .where(BookingInDb.resource_id == resource_id)
            .where(
                or_(
                    and_(BookingInDb.start <= start, start < BookingInDb.end),
                    and_(BookingInDb.start < end, end <= BookingInDb.end),
                )
            )
        )
        return (await self.db.execute(query)).scalars().all()
