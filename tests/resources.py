from src.modules.resources.models import ResourceInDb, RoomType


def test_create(client_admin):
    resource_data = {"name": "SuperDesk", "location": "FRANCE", "capacity": 5, "room_type": RoomType.DESK}
    response = client_admin.post("/resources/", json=resource_data)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "superdesk"
    assert data["location"] == "france"
    assert data["capacity"] == 5
    assert data["room_type"] == RoomType.DESK.value
    assert data["id"] is not None

    # Cannot create 2 resources with same email
    response = client_admin.post("/resources/", json=resource_data)
    assert response.status_code == 400


def test_list(session, client_user):
    response = client_user.get("/resources/")
    assert response.status_code == 200
    # Because of fixtures
    resource_count = len(response.json())

    resource_1 = ResourceInDb(name="conference room", location="france")
    resource_2 = ResourceInDb(name="war room", location="italy")
    resource_3 = ResourceInDb(name="cto desk", location="france - corse")
    session.add(resource_1)
    session.add(resource_2)
    session.add(resource_3)
    session.commit()
    session.refresh(resource_1)
    session.refresh(resource_2)
    session.refresh(resource_3)

    response = client_user.get("/resources/")
    assert response.status_code == 200
    assert len(response.json()) == resource_count + 3

    response = client_user.get("/resources/", params={"name": "room"})
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client_user.get("/resources/", params={"location": "it"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client_user.get("/resources/", params={"name": "ro", "location": "fra"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get(client_user, resource_1):
    response = client_user.get("/resources/9999")
    assert response.status_code == 404

    response = client_user.get(f"/resources/{resource_1.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == resource_1.id
    assert data["name"] == resource_1.name
    assert data["location"] == resource_1.location
    assert data["capacity"] == resource_1.capacity
    assert data["room_type"] == resource_1.room_type.value


def test_delete(session, client_admin, resource_1):
    response = client_admin.delete("/resources/9999")
    assert response.status_code == 404

    response = client_admin.delete(f"/resources/{resource_1.id}")
    assert response.status_code == 204
    assert not session.get(ResourceInDb, resource_1.id)
