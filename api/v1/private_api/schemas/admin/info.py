from pydantic import BaseModel
from typing import Optional

class UpdateSystemInfo(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    whatsapp_link: Optional[str] = None
    x_link: Optional[str] = None
    facebook_link: Optional[str] = None
    tiktok_link: Optional[str] = None
    instagram_link: Optional[str] = None

class AddMessage(BaseModel):
    title: str
    message: str
    is_active: bool

class EditMessage(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    is_active: Optional[bool] = None