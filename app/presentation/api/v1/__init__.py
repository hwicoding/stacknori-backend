from fastapi import APIRouter

from app.presentation.api.v1.routes import health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])

