from decimal import Decimal
from pydantic import BaseModel
from typing import Optional

from models.users import TxnType

class UpsertUser(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    number: Optional[str] = None
    pin: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_agent: Optional[bool] = None
    is_admin: Optional[bool] = None
    allow_api_access: Optional[bool] = None
    update_balance: Optional[UpdateUserBalance] = None

class UpdateUserBalance(BaseModel):
    amount: Decimal
    txn_type: TxnType
    message: str    