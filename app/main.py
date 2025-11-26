from fastapi import FastAPI

from app.core.config import Settings, get_settings
from app.presentation.api.v1.router import api_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """FastAPI application factory."""
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(api_router, prefix="/api")

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    return app


app = create_app()

