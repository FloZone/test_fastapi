from src.modules.users.models import Role, UserInDb


def test_create(client):
    user_data = {"name": "Toto", "email": "toto@test.com", "password": "pwd"}
    response = client.post("/users/", json=user_data)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Toto"
    assert data["email"] == "toto@test.com"
    assert data["role"] == Role.USER.value
    assert "password" not in data
    assert data["id"] is not None

    # Cannot create 2 users with same email
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400


def test_list(session, client_user):
    response = client_user.get("/users/")
    assert response.status_code == 200
    # Because of authenticated user
    user_count = len(response.json())

    user_1 = UserInDb(name="user1", email="user1@test.com", password="pwd")
    user_2 = UserInDb(name="user2", email="user2@test.com", password="pwd")
    session.add(user_1)
    session.add(user_2)
    session.commit()
    session.refresh(user_1)
    session.refresh(user_2)

    response = client_user.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == user_count + 2


def test_get(session, client_user):
    user_1 = UserInDb(name="user1", email="user1@test.com", password="pwd")
    session.add(user_1)
    session.commit()
    session.refresh(user_1)

    response = client_user.get("/users/9999")
    assert response.status_code == 404

    response = client_user.get(f"/users/{user_1.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == user_1.id
    assert data["name"] == user_1.name
    assert data["email"] == user_1.email
    assert data["role"] == user_1.role.value


def test_delete(session, client_admin):
    user_1 = UserInDb(name="user1", email="user1@test.com", password="pwd")
    session.add(user_1)
    session.commit()
    session.refresh(user_1)

    response = client_admin.delete("/users/9999")
    assert response.status_code == 404

    response = client_admin.delete(f"/users/{user_1.id}")
    assert response.status_code == 204
    assert not session.get(UserInDb, user_1.id)
