from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from petos_api.core.config import settings
from petos_api.logging import setup_logging
from petos_api.core.middleware import BFFGatewayMiddleware

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


def create_app() -> FastAPI:
    app = FastAPI(
        title="PetOS API",
        version=settings.app_version,
        lifespan=lifespan,
        # Disable docs in production
        docs_url="/docs" if settings.environment == "development" else None,
        redoc_url="/redoc" if settings.environment == "development" else None,
        openapi_url="/openapi.json" if settings.environment == "development" else None,
    )

    app.add_middleware(CorrelationIdMiddleware)

    # BFF Gateway: reject direct browser access to business endpoints.
    # Only health and dev docs are exempt.
    app.add_middleware(
        BFFGatewayMiddleware,
        bff_secret=settings.BFF_INTERNAL_SECRET,
        environment=settings.environment,
    )

    # CORS: the BFF origin is the only trusted browser origin.
    # No wildcard, no arbitrary credentialed requests from the browser.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=False,  # browser doesn't send credentials directly
        allow_methods=["GET"],  # only GET is safe for direct CORS; BFF handles the rest
        allow_headers=["*"],
    )

    from petos_api.api.health import router as health_router
    from petos_api.api.v1.auth import router as auth_router
    from petos_api.api.v1.organizations import router as organizations_router
    from petos_api.api.v1.projects import router as projects_router

    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(auth_router, prefix="/v1/auth", tags=["auth"])
    app.include_router(
        organizations_router, prefix="/v1/organizations", tags=["organizations"]
    )
    app.include_router(projects_router, prefix="/v1", tags=["projects"])

    return app


app = create_app()
