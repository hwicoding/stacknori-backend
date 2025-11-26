"""
Seed script to create initial admin user.

Usage:
    python scripts/seed_admin.py

Environment variables:
    ADMIN_EMAIL: Email for the admin user (default: admin@stacknori.com)
    ADMIN_PASSWORD: Password for the admin user (default: admin123456)
    FORCE_CREATE: If 'true', will create admin even if it exists (default: false)
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import get_settings
from app.core.database import Base
from app.core.security import get_password_hash
from app.infrastructure.db.models import UserModel


async def create_admin_user(
    session: AsyncSession, email: str, password: str, force: bool = False
) -> UserModel | None:
    """Create an admin user if it doesn't exist."""
    # Check if admin already exists
    from sqlalchemy import select

    stmt = select(UserModel).where(UserModel.email == email)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if not force:
            print(f"❌ Admin user with email '{email}' already exists.")
            print("   Set FORCE_CREATE=true to recreate it.")
            return None
        else:
            print(f"⚠️  Admin user '{email}' exists. Updating...")
            existing_user.hashed_password = get_password_hash(password)
            existing_user.is_superuser = True
            existing_user.is_active = True
            await session.commit()
            await session.refresh(existing_user)
            print(f"✅ Admin user '{email}' updated successfully.")
            return existing_user

    # Create new admin user
    admin_user = UserModel(
        email=email,
        hashed_password=get_password_hash(password),
        is_superuser=True,
        is_active=True,
    )
    session.add(admin_user)
    await session.commit()
    await session.refresh(admin_user)
    print(f"✅ Admin user '{email}' created successfully.")
    return admin_user


async def main():
    """Main entry point for seed script."""
    settings = get_settings()

    # Get admin credentials from environment
    admin_email = os.getenv("ADMIN_EMAIL", "admin@stacknori.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123456")
    force_create = os.getenv("FORCE_CREATE", "false").lower() == "true"

    print("🌱 Starting admin user seed...")
    print(f"   Email: {admin_email}")
    print(f"   Force create: {force_create}")

    # Create async engine and session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with async_session() as session:
            await create_admin_user(session, admin_email, admin_password, force_create)
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

    print("✨ Seed completed!")


if __name__ == "__main__":
    asyncio.run(main())

