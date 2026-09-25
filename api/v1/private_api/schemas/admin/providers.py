from pydantic import BaseModel
from typing import Optional

from models.admin import PaymentProviderName, ProviderType

class UpsertCredentials(BaseModel):
    account_or_business_id: Optional[str] = None
    token_or_api_key: Optional[str] = None
    username_or_public_key: Optional[str] = None
    password_or_secret_key: Optional[str] = None

class UpsertProvider(BaseModel):
    provider_name: Optional[str] = None
    provider_type: ProviderType | PaymentProviderName
    base_url: Optional[str] = None
    credentials: Optional[UpsertCredentials] = None