from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import root_routers, v1_routers
from app.core.settings import get_settings

# Remove auto-generated 422 errors from redoc and swagger docs
_openapi = FastAPI.openapi


def custom_openapi(self: FastAPI):
    _openapi(self)

    for _, method_item in self.openapi_schema.get("paths").items():
        for _, param in method_item.items():
            responses = param.get("responses")
            # remove 422 response, also can remove other status code
            if "422" in responses:
                del responses["422"]

    return self.openapi_schema


FastAPI.openapi = custom_openapi

# Application instance
app = FastAPI()

# Endpoints
app.include_router(root_routers, prefix=get_settings().API_PATH)
app.include_router(v1_routers, prefix=get_settings().API_V1_PATH)


# All int validation errors now return 400 error instead of 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )
