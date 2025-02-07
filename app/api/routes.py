from fastapi import APIRouter

from app.api.root.endpoints import router as root_router
from app.api.v1.booking import router as booking_router
from app.api.v1.resource import router as resource_router
from app.api.v1.user import router as user_router

# Root endpoints
root_routers = APIRouter()

for router in [root_router]:
    root_routers.include_router(router)


# V1 endpoints
v1_routers = APIRouter()

for router in [booking_router, resource_router, user_router]:
    v1_routers.include_router(router)
