from fastapi import APIRouter

from app.presentation.api.v1.routes import auth, health, materials, progress, roadmap

api_router = APIRouter(prefix="/v1")
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router)
api_router.include_router(roadmap.router)
api_router.include_router(materials.router)
api_router.include_router(progress.router)

