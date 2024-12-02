from datetime import datetime, timedelta

import pytz

from src.modules.bookings.models import BookingInDb


def test_create(client_user, resource_1):
    now = datetime.now(pytz.utc)
    start_future = now + timedelta(hours=1)
    end_future = now + timedelta(hours=2)

    booking_data = {
        "title": "Booking1",
        "resource_id": resource_1.id,
        "start": str(start_future),
        "end": str(end_future),
    }
    response = client_user.post("/bookings/", json=booking_data)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Booking1"
    assert data["id"] is not None


def test_list_user(session, client_user):
    response = client_user.get("/bookings/")
    assert response.status_code == 200
    # Because of fixtures
    booking_count = len(response.json())

    booking_1 = BookingInDb(name="booking1")
    booking_2 = BookingInDb(name="booking2")
    session.add(booking_1)
    session.add(booking_2)
    session.commit()
    session.refresh(booking_1)
    session.refresh(booking_2)

    response = client_user.get("/bookings/")
    assert response.status_code == 200
    assert len(response.json()) == booking_count + 2


def test_list_admin(session, client_user):
    response = client_user.get("/bookings/")
    assert response.status_code == 200
    # Because of fixtures
    booking_count = len(response.json())

    booking_1 = BookingInDb(name="booking1")
    booking_2 = BookingInDb(name="booking2")
    session.add(booking_1)
    session.add(booking_2)
    session.commit()
    session.refresh(booking_1)
    session.refresh(booking_2)

    response = client_user.get("/bookings/")
    assert response.status_code == 200
    assert len(response.json()) == booking_count + 2


def test_list_all(session, client_admin):
    response = client_admin.get("/bookings/")
    assert response.status_code == 200
    # Because of fixtures
    booking_count = len(response.json())

    booking_1 = BookingInDb(name="booking1")
    booking_2 = BookingInDb(name="booking2")
    session.add(booking_1)
    session.add(booking_2)
    session.commit()
    session.refresh(booking_1)
    session.refresh(booking_2)

    response = client_admin.get("/bookings/")
    assert response.status_code == 200
    assert len(response.json()) == booking_count + 2


def test_get_user(session, client_user, booking):
    response = client_user.get("/bookings/9999")
    assert response.status_code == 404

    response = client_user.get(f"/bookings/{booking.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking.id
    assert data["name"] == booking.name
    assert data["location"] == booking.location
    assert data["capacity"] == booking.capacity
    assert data["room_type"] == booking.room_type.value


def test_get_admin(session, client_user, booking):
    response = client_user.get("/bookings/9999")
    assert response.status_code == 404

    response = client_user.get(f"/bookings/{booking.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking.id
    assert data["name"] == booking.name
    assert data["location"] == booking.location
    assert data["capacity"] == booking.capacity
    assert data["room_type"] == booking.room_type.value


def test_update_user(session, client_user, booking):
    response = client_user.get("/bookings/9999")
    assert response.status_code == 404

    response = client_user.get(f"/bookings/{booking.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking.id
    assert data["name"] == booking.name
    assert data["location"] == booking.location
    assert data["capacity"] == booking.capacity
    assert data["room_type"] == booking.room_type.value


def test_update_admin(session, client_user, booking):
    response = client_user.get("/bookings/9999")
    assert response.status_code == 404

    response = client_user.get(f"/bookings/{booking.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking.id
    assert data["name"] == booking.name
    assert data["location"] == booking.location
    assert data["capacity"] == booking.capacity
    assert data["room_type"] == booking.room_type.value


def test_delete_user(session, client_admin, booking):
    response = client_admin.delete("/bookings/9999")
    assert response.status_code == 404

    response = client_admin.delete(f"/bookings/{booking.id}")
    assert response.status_code == 204
    assert not session.get(BookingInDb, booking.id)


def test_delete_admin(session, client_admin, booking):
    response = client_admin.delete("/bookings/9999")
    assert response.status_code == 404

    response = client_admin.delete(f"/bookings/{booking.id}")
    assert response.status_code == 204
    assert not session.get(BookingInDb, booking.id)
