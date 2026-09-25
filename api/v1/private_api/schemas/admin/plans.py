from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel

from models.admin import ChargesType, PaymentProviderName
from models.plans.disco import DiscoType
from models.plans.network import DataSize, DataType, DiscountType

class PlanQuery(BaseModel):
    id: Optional[int] = None
    page: Optional[int] = 1
    limit: Optional[int] = 20
    search: str = ""
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None

class UpsertProviderPlanSchema(BaseModel):
    plan_id: Optional[int] = None
    provider_name: Optional[str] = None
    provider_plan_id: Optional[str] = None

class UpsertPlanSchema(BaseModel):
    biller_id: Optional[int] = None
    type: Optional[DataType | DiscoType] = None
    name: Optional[str] = None
    size: Optional[DataSize] = None
    price: Optional[Decimal] = None
    minimum_amount: Optional[Decimal] = None
    maximum_amount: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    discount_type: Optional[DiscountType] = None
    agent_discount: Optional[Decimal] = None
    agent_discount_type: Optional[DiscountType] = None
    api_discount: Optional[Decimal] = None
    api_discount_type: Optional[DiscountType] = None
    description: Optional[str] = None
    validity: Optional[str] = None
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    vend_from: Optional[str] = None
    linked_plan: Optional[UpsertProviderPlanSchema] = None

class UpsertProviderBillerSchema(BaseModel):
    biller_id: Optional[int] = None
    provider_name: Optional[str] = None
    provider_biller_id: Optional[str] = None

class UpsertBillerSchema(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    is_active: Optional[bool] =  None
    linked_biller: Optional[UpsertProviderBillerSchema] = None

class PlanControlSchema(BaseModel):
    biller_id: int
    plan_type: DataType | DiscoType | None = None
    is_active: Optional[bool] = None
    vend_from: Optional[str] = None

class UpsertPGWPlanSchema(BaseModel):
    bank_name: Optional[str] = None
    provider: Optional[PaymentProviderName] = None
    charges_type: Optional[ChargesType] = None
    flat: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    capped: Optional[Decimal] = None
    is_active: Optional[bool] = None
    bank_code: Optional[str] = None

class AdminIDs(BaseModel):
    nin: Optional[str] = None
    bvn: Optional[str] = None