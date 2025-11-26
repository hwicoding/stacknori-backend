from fastapi import APIRouter

from app.presentation.api.v1.routes import auth, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router)

