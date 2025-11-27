from datetime import datetime

from pydantic import BaseModel


class MaterialScrap(BaseModel):
    id: int
    user_id: int
    material_id: int
    created_at: datetime

    class Config:
        from_attributes = True

