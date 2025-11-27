from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import Settings, get_settings
from app.presentation.api.v1.router import api_router


def custom_openapi(app: FastAPI):
    """OpenAPI 스키마 커스터마이징"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="""
## Stacknori API

학습 로드맵 및 자료 큐레이션 서비스를 위한 RESTful API입니다.

### 주요 기능
- **인증**: JWT 기반 사용자 인증 및 권한 관리
- **로드맵**: 분야별 학습 로드맵 계층 구조 제공
- **자료**: 검색 가능한 학습 자료 관리
- **진도**: 사용자별 학습 진도 추적 및 통계

### 인증
모든 API 엔드포인트는 JWT 토큰 인증이 필요합니다 (헬스체크 제외).
`/api/v1/auth/login`에서 토큰을 발급받은 후, 요청 헤더에 `Authorization: Bearer <token>`을 포함하세요.
        """,
        routes=app.routes,
    )

    # 예제 응답 추가
    openapi_schema["components"]["schemas"]["TokenPair"]["example"] = {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
    }

    openapi_schema["components"]["schemas"]["RoadmapListResponse"]["example"] = {
        "roadmaps": [
            {
                "id": 1,
                "category": "frontend",
                "name": "Frontend Basics",
                "level": 1,
                "description": "Frontend fundamentals",
                "parent_id": None,
                "is_completed": False,
                "children": [
                    {
                        "id": 2,
                        "category": "frontend",
                        "name": "HTML/CSS",
                        "level": 2,
                        "description": "HTML and CSS basics",
                        "parent_id": 1,
                        "is_completed": True,
                        "children": [],
                    }
                ],
            }
        ]
    }

    openapi_schema["components"]["schemas"]["MaterialListResponse"]["example"] = {
        "materials": [
            {
                "id": 1,
                "title": "FastAPI Tutorial",
                "url": "https://example.com/fastapi",
                "difficulty": "beginner",
                "type": "document",
                "source": "Example Source",
                "summary": "FastAPI introduction",
                "keywords": ["fastapi", "python", "api"],
                "is_scrapped": False,
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 100,
            "total_pages": 5,
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def create_app(settings: Settings | None = None) -> FastAPI:
    """FastAPI application factory."""
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.openapi = lambda: custom_openapi(app)  # type: ignore

    app.include_router(api_router, prefix="/api")

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "environment": settings.app_env}

    return app


app = create_app()

