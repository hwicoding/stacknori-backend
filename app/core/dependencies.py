from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.database import get_db
from app.domain.entities import User
from app.infrastructure.repositories.material_repository import (
    MaterialRepository,
    MaterialScrapRepository,
)
from app.infrastructure.repositories.progress_repository import (
    UserProgressRepository,
)
from app.infrastructure.repositories.roadmap_repository import RoadmapRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.usecases.auth import AuthService
from app.usecases.material import SearchMaterialsUseCase, ToggleMaterialScrapUseCase
from app.usecases.progress import GetUserProgressUseCase, UpdateProgressUseCase
from app.usecases.roadmap import GetRoadmapsUseCase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_user_repository(session=Depends(get_db)) -> UserRepository:
    return UserRepository(session)


async def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.get_current_user(token)


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency to require admin (superuser) access."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def get_roadmap_repository(
    session=Depends(get_db),
) -> RoadmapRepository:
    return RoadmapRepository(session)


async def get_progress_repository(
    session=Depends(get_db),
) -> UserProgressRepository:
    return UserProgressRepository(session)


async def get_material_repository(
    session=Depends(get_db),
) -> MaterialRepository:
    return MaterialRepository(session)


async def get_material_scrap_repository(
    session=Depends(get_db),
) -> MaterialScrapRepository:
    return MaterialScrapRepository(session)


async def get_roadmap_usecase(
    roadmap_repo: RoadmapRepository = Depends(get_roadmap_repository),
    progress_repo: UserProgressRepository = Depends(get_progress_repository),
) -> GetRoadmapsUseCase:
    return GetRoadmapsUseCase(roadmap_repo, progress_repo)


async def get_update_progress_usecase(
    roadmap_repo: RoadmapRepository = Depends(get_roadmap_repository),
    material_repo: MaterialRepository = Depends(get_material_repository),
    progress_repo: UserProgressRepository = Depends(get_progress_repository),
) -> UpdateProgressUseCase:
    return UpdateProgressUseCase(roadmap_repo, material_repo, progress_repo)


async def get_progress_overview_usecase(
    progress_repo: UserProgressRepository = Depends(get_progress_repository),
) -> GetUserProgressUseCase:
    return GetUserProgressUseCase(progress_repo)


async def get_material_search_usecase(
    repository: MaterialRepository = Depends(get_material_repository),
) -> SearchMaterialsUseCase:
    return SearchMaterialsUseCase(repository)


async def get_material_scrap_usecase(
    scrap_repo: MaterialScrapRepository = Depends(get_material_scrap_repository),
    material_repo: MaterialRepository = Depends(get_material_repository),
) -> ToggleMaterialScrapUseCase:
    return ToggleMaterialScrapUseCase(scrap_repo, material_repo)
