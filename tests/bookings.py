from datetime import datetime, timedelta

from src.modules.bookings.models import BookingInDb


def test_create(client_user, resource_1):
    booking_data = {"title": "Booking1", "resource_id": resource_1.id}
    now = datetime.now().astimezone()
    start_past = (now - timedelta(hours=2)).isoformat()
    end_past = (now - timedelta(hours=1)).isoformat()
    start_future_1 = (now + timedelta(hours=1)).isoformat()
    middle_1 = (now + timedelta(hours=1, minutes=30)).isoformat()
    end_future_1 = (now + timedelta(hours=2)).isoformat()
    start_future_2 = (now + timedelta(hours=2)).isoformat()
    end_future_2 = (now + timedelta(hours=3)).isoformat()
    start_future_3 = (now + timedelta(hours=3)).isoformat()
    end_future_3 = (now + timedelta(hours=4)).isoformat()

    # Booking in the past
    booking_data["start"] = start_past
    booking_data["end"] = end_past
    response = client_user.post("/bookings/", json=booking_data)
    assert response.status_code == 400

    # End date before start date
    booking_data["start"] = end_future_1
    booking_data["end"] = start_future_1
    response = client_user.post("/bookings/", json=booking_data)
    assert response.status_code == 400

    # First booking
    booking_data["start"] = start_future_1
    booking_data["end"] = end_future_1
    response = client_user.post("/bookings/", json=booking_data)
    data = response.json()
    assert response.status_code == 200
    assert data["title"] == "Booking1"
    assert data["id"] is not None

    # Second booking
    booking_data["start"] = start_future_3
    booking_data["end"] = end_future_3
    response = client_user.post("/bookings/", json=booking_data)
    assert response.status_code == 200

    # Not available
    booking_data["start"] = middle_1
    booking_data["end"] = end_future_2
    response = client_user.post("/bookings/", json=booking_data)
    assert response.status_code == 400

    # Third booking
    booking_data["start"] = start_future_2
    booking_data["end"] = end_future_2
    response = client_user.post("/bookings/", json=booking_data)
    assert response.status_code == 200


def test_list(session, client_user, base_user, base_admin, resource_1):
    response = client_user.get("/bookings/")
    assert response.status_code == 200
    # Because of fixtures
    booking_count = len(response.json())

    now = datetime.now().astimezone()
    t1 = now + timedelta(days=10, hours=0)
    t2 = now + timedelta(days=10, hours=1)
    t3 = now + timedelta(days=10, hours=2)
    t4 = now + timedelta(days=10, hours=3)
    booking_1 = BookingInDb(title="booking 1", owner_id=base_user.id, resource_id=resource_1.id, start=t1, end=t2)
    booking_2 = BookingInDb(title="booking 2", owner_id=base_user.id, resource_id=resource_1.id, start=t2, end=t3)
    booking_3 = BookingInDb(title="booking 3", owner_id=base_admin.id, resource_id=resource_1.id, start=t3, end=t4)
    session.add(booking_1)
    session.add(booking_2)
    session.add(booking_3)
    session.commit()
    session.refresh(booking_1)
    session.refresh(booking_2)
    session.refresh(booking_3)

    response = client_user.get("/bookings/")
    assert response.status_code == 200
    assert len(response.json()) == booking_count + 2


def test_list_all(session, client_admin, base_user, base_admin, resource_1):
    response = client_admin.get("/bookings/all")
    assert response.status_code == 200
    # Because of fixtures
    booking_count = len(response.json())

    now = datetime.now().astimezone()
    t1 = now + timedelta(days=10, hours=0)
    t2 = now + timedelta(days=10, hours=1)
    t3 = now + timedelta(days=10, hours=2)
    t4 = now + timedelta(days=10, hours=3)
    booking_1 = BookingInDb(title="booking 1", owner_id=base_user.id, resource_id=resource_1.id, start=t1, end=t2)
    booking_2 = BookingInDb(title="booking 2", owner_id=base_user.id, resource_id=resource_1.id, start=t2, end=t3)
    booking_3 = BookingInDb(title="booking 3", owner_id=base_admin.id, resource_id=resource_1.id, start=t3, end=t4)
    session.add(booking_1)
    session.add(booking_2)
    session.add(booking_3)
    session.commit()
    session.refresh(booking_1)
    session.refresh(booking_2)
    session.refresh(booking_3)

    response = client_admin.get("/bookings/all")
    assert response.status_code == 200
    assert len(response.json()) == booking_count + 3


def test_get_user(client_user, booking_user, booking_admin):
    response = client_user.get("/bookings/9999")
    assert response.status_code == 404

    response = client_user.get(f"/bookings/{booking_admin.id}")
    assert response.status_code == 404

    response = client_user.get(f"/bookings/{booking_user.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking_user.id
    assert data["title"] == booking_user.title
    assert datetime.fromisoformat(data["start"]) == booking_user.start
    assert datetime.fromisoformat(data["end"]) == booking_user.end


def test_get_admin(client_admin, booking_user, booking_admin):
    response = client_admin.get("/bookings/9999")
    assert response.status_code == 404

    response = client_admin.get(f"/bookings/{booking_admin.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking_admin.id
    assert data["title"] == booking_admin.title
    assert datetime.fromisoformat(data["start"]) == booking_admin.start
    assert datetime.fromisoformat(data["end"]) == booking_admin.end

    response = client_admin.get(f"/bookings/{booking_user.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking_user.id
    assert data["title"] == booking_user.title
    assert datetime.fromisoformat(data["start"]) == booking_user.start
    assert datetime.fromisoformat(data["end"]) == booking_user.end


def test_update_user(client_user, booking_user, booking_admin, resource_2):
    booking_data = {
        "title": booking_user.title,
        "resource_id": booking_user.resource_id,
        "start": booking_user.start.astimezone().isoformat(),
        "end": booking_user.end.astimezone().isoformat(),
    }
    response = client_user.put("/bookings/9999", json=booking_data)
    assert response.status_code == 404

    response = client_user.put(f"/bookings/{booking_admin.id}", json=booking_data)
    assert response.status_code == 404

    # Update title
    booking_data["title"] = booking_data["title"] + "_edited"
    response = client_user.put(f"/bookings/{booking_user.id}", json=booking_data)
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking_user.id
    assert data["title"] == booking_data["title"]
    assert data["resource_id"] == booking_data["resource_id"]
    assert datetime.fromisoformat(data["start"]) == booking_user.start
    assert datetime.fromisoformat(data["end"]) == booking_user.end

    # Update end
    new_date = booking_user.end + timedelta(hours=1)
    booking_data["end"] = new_date.astimezone().isoformat()
    response = client_user.put(f"/bookings/{booking_user.id}", json=booking_data)
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking_user.id
    assert data["title"] == booking_data["title"]
    assert data["resource_id"] == booking_data["resource_id"]
    assert datetime.fromisoformat(data["start"]) == booking_user.start
    assert datetime.fromisoformat(data["end"]) == new_date

    # Not available
    booking_data["end"] = booking_admin.end.astimezone().isoformat()
    response = client_user.put(f"/bookings/{booking_user.id}", json=booking_data)
    assert response.status_code == 400

    # Change resource
    booking_data["end"] = booking_user.end.astimezone().isoformat()
    booking_data["resource_id"] = resource_2.id
    response = client_user.put(f"/bookings/{booking_user.id}", json=booking_data)
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking_user.id
    assert data["title"] == booking_data["title"]
    assert data["resource_id"] == booking_data["resource_id"]


def test_update_admin(client_admin, booking_user, booking_admin):
    booking_data = {
        "title": booking_user.title + "_edited",
        "resource_id": booking_user.resource_id,
        "start": booking_user.start.astimezone().isoformat(),
        "end": booking_user.end.astimezone().isoformat(),
    }
    response = client_admin.put("/bookings/9999", json=booking_data)
    assert response.status_code == 404

    # Update other user booking
    response = client_admin.put(f"/bookings/{booking_user.id}", json=booking_data)
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking_user.id
    assert data["title"] == booking_data["title"]
    assert data["resource_id"] == booking_data["resource_id"]

    booking_data = {
        "title": booking_admin.title + "_edited",
        "resource_id": booking_admin.resource_id,
        "start": booking_admin.start.astimezone().isoformat(),
        "end": booking_admin.end.astimezone().isoformat(),
    }
    # Update admin booking
    response = client_admin.put(f"/bookings/{booking_admin.id}", json=booking_data)
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == booking_admin.id
    assert data["title"] == booking_data["title"]
    assert data["resource_id"] == booking_data["resource_id"]


def test_delete_user(session, client_user, base_user, resource_1, booking_user, booking_admin):
    response = client_user.delete("/bookings/9999")
    assert response.status_code == 404

    response = client_user.delete(f"/bookings/{booking_admin.id}")
    assert response.status_code == 404

    # Delete future booking
    response = client_user.delete(f"/bookings/{booking_user.id}")
    assert response.status_code == 204
    assert not session.get(BookingInDb, booking_user.id)

    # Delete current booking
    now = datetime.now().astimezone()
    t1 = now - timedelta(minutes=5)
    t2 = now + timedelta(minutes=5)
    booking = BookingInDb(title="booking", owner_id=base_user.id, resource_id=resource_1.id, start=t1, end=t2)
    session.add(booking)
    session.commit()
    session.refresh(booking)
    response = client_user.delete(f"/bookings/{booking.id}")
    assert response.status_code == 204
    assert not session.get(BookingInDb, booking.id)

    # Cannot delete past booking
    now = datetime.now().astimezone()
    t1 = now - timedelta(hours=2)
    t2 = now - timedelta(hours=1)
    booking = BookingInDb(title="booking", owner_id=base_user.id, resource_id=resource_1.id, start=t1, end=t2)
    session.add(booking)
    session.commit()
    session.refresh(booking)
    response = client_user.delete(f"/bookings/{booking.id}")
    assert response.status_code == 400


def test_delete_admin(session, client_admin, booking_user, booking_admin):
    response = client_admin.delete("/bookings/9999")
    assert response.status_code == 404

    response = client_admin.delete(f"/bookings/{booking_admin.id}")
    assert response.status_code == 204
    assert not session.get(BookingInDb, booking_admin.id)

    response = client_admin.delete(f"/bookings/{booking_user.id}")
    assert response.status_code == 204
    assert not session.get(BookingInDb, booking_user.id)
