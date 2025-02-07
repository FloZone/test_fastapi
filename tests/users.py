import pytest

from app.models.user_model import Role, UserInDb


def test_create(client):
    user_data = {"name": "Toto", "email": "toto@test.com", "password": "pwd", "role": Role.USER.value}
    response = client.post("/api/v1/users/", json=user_data)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Toto"
    assert data["email"] == "toto@test.com"
    assert data["role"] == Role.USER.value
    assert "password" not in data
    assert data["id"] is not None

    # Cannot create 2 users with same email
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list(session, client_user):
    response = client_user.get("/api/v1/users/")
    assert response.status_code == 200
    # Because of fixtures
    user_count = len(response.json())

    user_1 = UserInDb(name="user1", email="user1@test.com", password="pwd")
    user_2 = UserInDb(name="user2", email="user2@test.com", password="pwd")
    session.add(user_1)
    session.add(user_2)
    await session.commit()
    await session.refresh(user_1)
    await session.refresh(user_2)

    response = client_user.get("/api/v1/users/")
    assert response.status_code == 200
    assert len(response.json()) == user_count + 2


def test_get(session, client_user, base_user):
    response = client_user.get("/api/v1/users/9999")
    assert response.status_code == 404

    response = client_user.get(f"/api/v1/users/{base_user.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == base_user.id
    assert data["name"] == base_user.name
    assert data["email"] == base_user.email
    assert data["role"] == base_user.role.value


@pytest.mark.asyncio
async def test_delete(session, client_admin, base_user):
    response = client_admin.delete("/api/v1/users/9999")
    assert response.status_code == 404

    response = client_admin.delete(f"/api/v1/users/{base_user.id}")
    assert response.status_code == 204
    assert not await session.get(UserInDb, base_user.id)
