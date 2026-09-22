from pydantic import BaseModel
from typing import Optional

class AddPlanRoute(BaseModel):
    plan_id: int
    provider: str

class EditPlanRoute(BaseModel):
    plan_id: Optional[int] = None
    provider: Optional[str] = None