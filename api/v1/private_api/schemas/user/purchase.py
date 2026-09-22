from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Literal, Optional, Text

from sqlalchemy import Numeric

from models.users import Status


class PurchaseSchema(BaseModel):
    biller_id: Optional[str] = None
    plan_id: Optional[str] = None
    plan_type: Optional[str] = None
    beneficiary: str
    amount: Optional[Decimal] = None

class PurchaseResponse(BaseModel):
    status: Literal[Status.SUCCESS, Status.FAIL, Status.PENDING]
    cash_back: Decimal = Field(examples=[Decimal("10.00")])
    message: str = Field(examples=["2GB was successful"])
    api_response: str
    beneficiary: str = Field(examples=["09169728552"])
    product: str
    amount: Decimal = Field(examples=[Decimal("500.00")])
    old_balance: Decimal = Field(examples=[Decimal("5000.00")])
    new_balance: Decimal = Field(examples=[Decimal("4500.00")])
    reference: str
    request_id: str