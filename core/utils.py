from decimal import Decimal
from enum import Enum
from typing import Optional, TypedDict
from uuid import uuid4
from datetime import datetime
import random, httpx, secrets
from pydantic import BaseModel
from models.users import KYCStatus, Status, User
from models.plans.network import DiscountType

class TxnDetails(BaseModel):
    service: str
    service_type: Optional[str] = None
    service_provider: str
    beneficiary: str
    value: Decimal
    product: str
    request_id: Optional[str] = None

class PaymentExecutorResponse(TypedDict):
    cash_back: Decimal
    amount: Decimal
    old_balance: Decimal
    new_balance: Decimal
    reference: str

class ProviderResponse(BaseModel):
    status: Status
    api_response: Optional[str] = None
    token: Optional[str] = None
    provider_name: Optional[str] = None
    provider_ref: Optional[str] = None

class ProviderAuthResponse(TypedDict):
    account_or_business_id: str | None
    token_or_api_key: str | None
    username_or_public_key: str | None
    password_or_secret_key: str | None

class CredentialsToAuth(TypedDict):
    account_or_business_id: str | None
    token_or_api_key: str | None
    username_or_public_key: str | None
    password_or_secret_key: str | None

class AuthResponse(TypedDict):
    business_id: str | None
    public_key: str | None
    api_key: str | None
    secret_key: str | None

class BankAccount(BaseModel):
    bank_name: str 
    account_number: str 
    account_name: str
    account_reference: str
    bank_code: str
    provider: str

class PaymentRequest(BaseModel):
    email: str
    amount: Decimal
    account_number: str
    api_response: str
    provider: str
    provider_reference: str

class KYCResponse(TypedDict):
    status: KYCStatus
    first_name: str
    middle_name: str
    last_name: str
    full_name: str
    phone_number: str
    email: str
    gender: str
    state_of_origin: str
    nationality: str
    lga_of_origin: str
    address: str
    date_of_birth: str

def generate_reference(prefix: str):
    now = datetime.now()
    reference = f'{prefix}|{now:%Y%m%d}|{now:%H%M}|{uuid4().hex[:8]}'
    return reference.upper()

def generate_otp():
    return random.randint(111111, 999999)

def generate_api_key():
    return "sk_" + secrets.token_urlsafe(32)

def get_cash_back(user: User, plan: object):

    discount: Decimal = (getattr(plan, 'agent_discount', 0) if user.is_agent else getattr(plan, 'discount', 0)) or 0
    discount_type = (getattr(plan, 'agent_discount_type', DiscountType.FLAT.value) if user.is_agent else getattr(plan, 'discount_type', DiscountType.FLAT.value)) or DiscountType.FLAT.value

    return (f'₦{discount.normalize()}' if discount_type == DiscountType.FLAT.value else f'{discount.normalize()}%') if discount else None

class CredentialsType(str, Enum):
    PIN = "pin"
    PASSWORD = "password"


async def request(method: str, url: str, headers: dict | None = None, auth: tuple | None = None, body: dict | None = None):
    async with httpx.AsyncClient(timeout=120, auth=auth) as client:
        return await client.request(method=method, url=url, headers=headers, json=body)