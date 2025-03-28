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
        ("get", "/api/", Access.OPEN),
        ("get", "/api/me", Access.USER),
        # Users endpoints
        ("post", "/api/v1/users/", Access.OPEN),
        ("get", "/api/v1/users/", Access.USER),
        ("get", "/api/v1/users/1", Access.USER),
        ("delete", "/api/v1/users/1", Access.ADMIN),
        # Resources endpoints
        ("post", "/api/v1/resources/", Access.ADMIN),
        ("get", "/api/v1/resources/", Access.USER),
        ("get", "/api/v1/resources/1", Access.USER),
        ("put", "/api/v1/resources/1", Access.ADMIN),
        ("delete", "/api/v1/resources/1", Access.ADMIN),
        # Bookings endpoints
        ("post", "/api/v1/bookings/", Access.USER),
        ("get", "/api/v1/bookings/", Access.USER),
        ("get", "/api/v1/bookings/all", Access.ADMIN),
        ("get", "/api/v1/bookings/1", Access.USER),
        ("put", "/api/v1/bookings/1", Access.USER),
        ("delete", "/api/v1/bookings/1", Access.USER),
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
