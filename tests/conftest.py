import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import Settings
from app.core.database import Base
from app.infrastructure.db.models import UserModel
from app.main import create_app


class TestBase(DeclarativeBase):
    pass


@pytest.fixture
def test_settings() -> Settings:
    """테스트용 설정 (SQLite in-memory DB 사용)"""
    return Settings(
        app_name="Stacknori API Test",
        app_env="test",
        app_debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        secret_key="test-secret-key-for-testing-only-not-for-production",
        algorithm="HS256",
        access_token_expire_minutes=60,
        refresh_token_expire_minutes=60 * 24 * 14,
    )


@pytest.fixture
async def test_db_session(test_settings: Settings):
    """테스트용 DB 세션 (트랜잭션 롤백)"""
    engine = create_async_engine(
        test_settings.database_url,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_client(test_db_session: AsyncSession):
    """FastAPI 테스트 클라이언트"""
    from app.core.database import get_db
    
    app = create_app()
    
    # 의존성 오버라이드: 테스트 DB 세션 사용
    async def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_user(test_db_session: AsyncSession):
    """테스트용 샘플 사용자 생성"""
    from app.core.security import get_password_hash
    
    user = UserModel(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_superuser=False,
    )
    test_db_session.add(user)
    await test_db_session.flush()
    await test_db_session.refresh(user)
    return user

