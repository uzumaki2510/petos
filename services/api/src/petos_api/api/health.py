from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from petos_api.config import settings
from petos_api.database import check_postgres
from petos_api.redis_client import check_redis

router = APIRouter()


class ReadinessResponse(BaseModel):
    status: str
    postgres: str
    redis: str
    version: str


@router.get("/health/live")
async def live() -> dict:
    return {"status": "ok"}


@router.get("/health/ready", response_model=ReadinessResponse)
async def ready() -> ReadinessResponse:
    pg_ok = await check_postgres()
    redis_ok = await check_redis()

    if not pg_ok or not redis_ok:
        raise HTTPException(status_code=503, detail="Service Unavailable")

    return ReadinessResponse(
        status="ok", postgres="ok", redis="ok", version=settings.app_version
    )
