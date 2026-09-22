from pydantic import BaseModel, EmailStr, Field, field_validator

class Register(BaseModel):
    name: str
    email: EmailStr
    number: str = Field(max_length=11, min_length=11)
    pin: str = Field(max_length=4, min_length=4)
    password: str = Field(min_length=8)

class Login(BaseModel):
    email: EmailStr
    password: str

class UpdatePassword(BaseModel):
    new_password: str
    confirm_new_password: str
