from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int | None = None
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

