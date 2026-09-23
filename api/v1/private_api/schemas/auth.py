from pydantic import BaseModel, EmailStr, Field, field_validator

class Register(BaseModel):
    name: str
    email: EmailStr
    number: str 
    pin: str 
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

class UpdatePassword(BaseModel):
    new_password: str
    confirm_new_password: str
