from pydantic import BaseModel
from models.users import Services

class UserTxnFilter(BaseModel):
    search: str = ""
    service: str = ""