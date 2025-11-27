from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MaterialScrap(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    material_id: int
    created_at: datetime

