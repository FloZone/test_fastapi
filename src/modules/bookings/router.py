from datetime import datetime

import pytz
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import and_, or_, select

from ...database import DBSession
from ...security import AllowRole, AuthenticatedUser
from ..users.models import Role
from .models import BookingIn, BookingInDb, BookingOut

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

# TODO create update() for future bookings
# TODO create tests


@router.post("/", responses={400: {"description": "Value error"}, 404: {"description": "Resource not found"}})
def create(booking: BookingIn, db: DBSession, current_user: AuthenticatedUser) -> BookingOut:
    """Book a resource."""
    input_data = booking.model_dump()

    resource_id = input_data["resource_id"]
    start = input_data["start"]
    end = input_data["end"]

    # TODO put this test on a method + use model_validate before
    # Search bookings scheduled during the start or the end date
    statement = (
        select(BookingInDb)
        .where(BookingInDb.resource_id == resource_id)
        .where(
            or_(
                and_(BookingInDb.start <= start, start < BookingInDb.end),
                and_(BookingInDb.start < end, end <= BookingInDb.end),
            )
        )
    )
    existing_bookings = db.exec(statement).all()
    if existing_bookings:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resource is not available on these dates")

    input_data["owner_id"] = current_user.id
    try:
        booking_db = BookingInDb.model_validate(input_data)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors()[0]["msg"])
    db.add(booking_db)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    db.refresh(booking_db)
    return booking_db


@router.get("/all")
def list_all(
    db: DBSession,
    current_user: AuthenticatedUser,
    offset: int = 0,
    limit: int = 100,
    _: bool = Depends(AllowRole([Role.ADMIN])),
) -> list[BookingInDb]:
    """[Admin] List all bookings."""
    bookings = db.exec(select(BookingInDb).offset(offset).limit(limit)).all()
    return bookings


@router.get("/")
def list(db: DBSession, current_user: AuthenticatedUser, offset: int = 0, limit: int = 100) -> list[BookingOut]:
    """List user bookings."""
    bookings = db.exec(
        select(BookingInDb).where(BookingInDb.owner_id == current_user.id).offset(offset).limit(limit)
    ).all()
    return bookings


@router.get("/{id}", responses={404: {"description": "Not found"}})
def get(id: int, db: DBSession, current_user: AuthenticatedUser) -> BookingOut:
    """Get a booking data."""
    booking = db.get(BookingInDb, id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # If user is not admin and try to access a booking that is not his own
    if current_user.role.value < Role.ADMIN.value and booking.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return booking


@router.delete(
    "/{id}", status_code=204, responses={400: {"description": "Value error"}, 404: {"description": "Not found"}}
)
def delete(
    id: int,
    db: DBSession,
    current_user: AuthenticatedUser,
):
    """Delete a current or future booking."""
    booking = db.get(BookingInDb, id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # If user is not admin and try to access a booking that is not his own
    if current_user.role.value < Role.ADMIN.value and booking.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # Can delete current or future booking but not past ones
    if booking.end < datetime.now(pytz.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel past bookings")

    db.delete(booking)
    db.commit()
