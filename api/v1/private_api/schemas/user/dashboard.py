from datetime import date
from pydantic import BaseModel
from typing import Optional

class VerifyKYC(BaseModel):
    id_number: str
    number: Optional[str] = None
    date_of_birth: Optional[date] = None