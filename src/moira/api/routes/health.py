from fastapi import APIRouter

from moira.core.config import settings

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }
