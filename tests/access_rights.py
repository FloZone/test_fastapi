from enum import Enum, auto

import pytest


class Access(Enum):
    OPEN = auto()
    USER = auto()
    ADMIN = auto()


@pytest.mark.parametrize("fastapi_client", ("client", "client_user", "client_admin"))
@pytest.mark.parametrize(
    "method,url,access",
    [
        # Main endpoints
        ("get", "/", Access.OPEN),
        ("get", "/me", Access.USER),
        # Users endpoints
        ("post", "/users/", Access.OPEN),
        ("get", "/users/", Access.USER),
        ("get", "/users/1", Access.USER),
        ("delete", "/users/1", Access.ADMIN),
        # Resources endpoints
        ("post", "/resources/", Access.ADMIN),
        ("get", "/resources/", Access.USER),
        ("get", "/resources/1", Access.USER),
        ("delete", "/resources/1", Access.ADMIN),
        # Bookings endpoints
        ("post", "/bookings/", Access.USER),
        ("get", "/bookings/", Access.USER),
        ("get", "/bookings/all", Access.ADMIN),
        ("get", "/bookings/1", Access.USER),
        ("put", "/bookings/1", Access.USER),
        ("delete", "/bookings/1", Access.USER),
    ],
)
def test_access_rights(fastapi_client, method, url, access, request):
    client = request.getfixturevalue(fastapi_client)
    response = client.request(method, url)

    if access == Access.OPEN:
        assert response.status_code != 401
    elif access == Access.USER:
        if fastapi_client == "client":
            assert response.status_code == 401
        elif fastapi_client == "client_user":
            assert response.status_code != 401
        elif fastapi_client == "client_admin":
            assert response.status_code != 401
    elif access == Access.ADMIN:
        if fastapi_client == "client":
            assert response.status_code == 401
        elif fastapi_client == "client_user":
            assert response.status_code == 401
        elif fastapi_client == "client_admin":
            assert response.status_code != 401
