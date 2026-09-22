from typing import Optional

from pydantic import BaseModel

class VTUPurchase(BaseModel):
    biller_id: Optional[int] = None
    plan_id: Optional[int] = None
    plan_type: Optional[str] = None
    beneficiary: Optional[str] = None
    request_id: Optional[str] = None