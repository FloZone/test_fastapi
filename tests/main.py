def test_hello_world(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World!"}


def test_login(client, base_user):
    response = client.post("/token", data={"username": "wrong_email", "password": "wrong_password"})
    assert response.status_code == 401

    response = client.post("/token", data={"username": base_user.email, "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None


def test_me(client_authenticated, base_user):
    response = client_authenticated.get("/me")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == base_user.id
    assert data["name"] == base_user.name
    assert data["email"] == base_user.email
