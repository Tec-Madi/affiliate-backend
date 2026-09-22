from pydantic import BaseModel

class UpdateCredentials(BaseModel):
    old_credential: str
    new_credential: str