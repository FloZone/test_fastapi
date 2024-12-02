from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from ...database import DBSession
from ...security import AllowRole, AuthenticatedUser
from ..resources.models import ResourceInDb
from ..users.models import Role
from .models import BookingIn, BookingInDb, BookingOut

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)


# TODO catch datetime_future error and return 400
@router.post("/", responses={400: {"description": "Value error"}, 404: {"description": "Resource not found"}})
def create(booking: BookingIn, db: DBSession, current_user: AuthenticatedUser) -> BookingOut:
    """Book a resource."""
    input_data = booking.model_dump()
    input_data["owner_id"] = current_user.id
    # Validate fields
    try:
        booking_db = BookingInDb.model_validate(input_data)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors()[0]["msg"])
    # Check if resource is available
    if not ResourceInDb.is_available(db, booking_db.resource_id, booking_db.start, booking_db.end):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resource is not available on these dates")
    # Save in DB and set FKs
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


@router.put("/{id}", responses={404: {"description": "Not found"}})
def update(id: int, booking: BookingIn, db: DBSession, current_user: AuthenticatedUser) -> BookingOut:
    """Update a booking data only for future booking."""
    booking_db = db.get(BookingInDb, id)
    if not booking_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # If user is not admin and try to access a booking that is not his own
    if current_user.role.value < Role.ADMIN.value and booking_db.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    # Can update future booking but not current or past ones
    if booking.end > datetime.now().astimezone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot update current or past bookings")

    update_data = booking.model_dump(exclude_unset=True)
    update_data["owner_id"] = current_user.id
    # Validate fields
    try:
        BookingInDb.model_validate(update_data)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.errors()[0]["msg"])
    # Check if resource is available
    if not ResourceInDb.is_available(db, update_data["resource_id"], update_data["start"], update_data["end"], id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resource is not available on these dates")

    # Save in DB
    booking_db.sqlmodel_update(update_data)
    db.add(booking_db)
    db.commit()
    db.refresh(booking_db)
    return booking_db


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
    if booking.end < datetime.now().astimezone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot cancel past bookings")

    db.delete(booking)
    db.commit()
