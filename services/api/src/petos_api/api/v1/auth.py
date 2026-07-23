from fastapi import APIRouter, Depends, Request, Response
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from petos_api.database import get_db
from petos_api.schemas.auth import RegisterRequest, LoginRequest
from petos_api.schemas.user import UserResponse
from petos_api.services.auth_service import AuthService
from petos_api.api.dependencies.auth import get_current_user
from petos_api.core.config import settings
from petos_api.core.rate_limit import (
    check_registration_rate_limits,
    check_login_rate_limits,
)

router = APIRouter()


def get_client_ip(request: Request) -> str:
    """
    Extract client IP for rate-limiting.

    The BFF sends X-PetOS-Client-IP together with the validated BFF secret.
    BFFGatewayMiddleware has already verified the secret before this code runs,
    so X-PetOS-Client-IP is trusted when present.

    If the header is absent (direct connection, e.g. health checks in local dev),
    we fall back to the TCP socket peer address.

    NOTE (local dev / Docker): Multiple browser users may appear to share a single
    IP because Docker bridges NAT traffic through the gateway address. Identity and
    combined rate-limit buckets still protect authentication in this case.
    """
    ip = request.headers.get("X-PetOS-Client-IP")
    if not ip:
        ip = request.client.host if request.client else "unknown"
    return ip


@router.post("/register", status_code=201, response_model=UserResponse)
async def register(
    req: RegisterRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ip = get_client_ip(request)
    await check_registration_rate_limits(ip, req.email)

    auth_service = AuthService(db)
    user_res, token = await auth_service.register(req)

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return user_res


@router.post("/login", response_model=UserResponse)
async def login(
    req: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    ip = get_client_ip(request)
    await check_login_rate_limits(ip, req.email)

    auth_service = AuthService(db)
    user_res, token = await auth_service.login(req)

    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return user_res


@router.post("/logout", status_code=204)
async def logout(
    request: Request, response: Response, db: Annotated[AsyncSession, Depends(get_db)]
):
    # All known Phase 3 cookie names — clear every one unconditionally.
    # The production __Host- cookie requires Secure=true and Path=/ with no Domain.
    DEV_COOKIE = "petos_session"
    PROD_COOKIE = "__Host-petos_session"
    _PHASE3_COOKIES = {DEV_COOKIE, PROD_COOKIE, settings.SESSION_COOKIE_NAME}

    # Try to revoke the server-side session using the first token we find.
    from petos_api.core.security import hash_session_token

    token = None
    for name in _PHASE3_COOKIES:
        token = request.cookies.get(name)
        if token:
            break

    if token:
        auth_service = AuthService(db)
        hashed_token = hash_session_token(token)
        try:
            await auth_service.logout(hashed_token)
        except Exception:
            pass  # idempotent — already revoked or not found

    # Clear every known cookie name so stale cookies are removed.
    for name in _PHASE3_COOKIES:
        if name == PROD_COOKIE:
            # __Host- cookies must be cleared with Secure=True and no Domain.
            response.delete_cookie(
                key=name, path="/", secure=True, httponly=True, samesite="lax"
            )
        else:
            response.delete_cookie(key=name, path="/", httponly=True, samesite="lax")
    return None


@router.get("/me", response_model=UserResponse)
async def get_me(user: Annotated[UserResponse, Depends(get_current_user)]):
    return user
