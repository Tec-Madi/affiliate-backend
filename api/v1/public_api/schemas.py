from typing import Optional
from decimal import Decimal

from pydantic import BaseModel

class VTUPurchase(BaseModel):
    biller_id: Optional[int] = None
    plan_id: Optional[int] = None
    plan_type: Optional[str] = None
    beneficiary: Optional[str] = None
    amount: Optional[Decimal] = None
    request_id: Optional[str] = None