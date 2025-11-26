from fastapi import APIRouter

from app.usecases.health_check import get_health_payload

router = APIRouter()


@router.get("/", summary="Health check")
async def read_health() -> dict[str, str]:
    return await get_health_payload()

