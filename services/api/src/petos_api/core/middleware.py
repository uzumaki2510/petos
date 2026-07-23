from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import secrets
import logging

logger = logging.getLogger(__name__)

HEALTH_PATHS = {"/health/live", "/health/ready"}
DEV_OPEN_PATHS = {"/docs", "/openapi.json", "/redoc"}


class BFFGatewayMiddleware(BaseHTTPMiddleware):
    """
    Enforces that all business API endpoints can only be called by the BFF.
    The BFF proves identity via X-PetOS-BFF-Secret header.
    Health and dev docs endpoints are always open.
    """

    def __init__(self, app, bff_secret: str, environment: str = "development"):
        super().__init__(app)
        self.bff_secret = bff_secret
        self.environment = environment

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Always allow health and liveness probes
        if path in HEALTH_PATHS:
            return await call_next(request)

        # Allow docs in development only
        if self.environment == "development" and path in DEV_OPEN_PATHS:
            return await call_next(request)

        # All other routes require valid BFF secret
        supplied = request.headers.get("X-PetOS-BFF-Secret", "")
        if not supplied:
            logger.warning(
                "Rejected request: missing BFF secret: method=%s path=%s",
                request.method,
                path,
            )
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=403,
                content={"code": "missing_bff_secret", "message": "Forbidden"},
            )

        if not secrets.compare_digest(supplied, self.bff_secret):
            logger.warning(
                "Rejected request: invalid BFF secret: method=%s path=%s",
                request.method,
                path,
            )
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=403,
                content={"code": "invalid_bff_secret", "message": "Forbidden"},
            )

        return await call_next(request)


class CSRFMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_origins: list[str]):
        super().__init__(app)
        self.allowed_origins = [o.rstrip("/") for o in allowed_origins]

    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            origin = request.headers.get("origin")
            referer = request.headers.get("referer")

            if referer and referer.endswith("/"):
                referer = referer[:-1]

            is_valid = False
            if origin and origin in self.allowed_origins:
                is_valid = True
            elif referer:
                for allowed in self.allowed_origins:
                    if referer.startswith(allowed):
                        is_valid = True
                        break

            if not is_valid:
                logger.warning(
                    "CSRF attempt rejected. Origin: %s, Referer: %s", origin, referer
                )
                raise HTTPException(
                    status_code=403, detail="CSRF token missing or incorrect"
                )

        return await call_next(request)
