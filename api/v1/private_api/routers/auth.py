from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.v1.private_api.schemas.auth import Register, UpdatePassword, Login
from core.database import get_db
from models.users import User
from services.auth.login import login_function
from services.auth.pin import pin_validator_function
from services.auth.register import register_function
from services.auth.reset_password import request_reset_password_function, validate_otp_function, change_password_function


auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication and Registeration']
)

@auth_router.post('/login')
def login(response: Response, data: Login, db: Session = Depends(get_db)):
    login = login_function(email=data.email, password=data.password, db=db)
    token = login['access_token']
    response.set_cookie(
        key='access_token',
        value=token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age= 60 * 60 * 24 * 30
    )

    return {
        'is_admin': login['is_admin'],
        'email': login['email'],
        'balance': login['balance']
    }

@auth_router.post('/logout')
def logout(response: Response, user: User = Depends(get_current_user)):
    response.delete_cookie(
        key='access_token',
        httponly=True,
        secure=False,
        samesite='lax'
    )
    return {'message': 'Logout Successful'}

@auth_router.post("/validate/{pin}")
def pin_validator(pin: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return pin_validator_function(user=user, db=db, pin=pin)

@auth_router.post('/register')
def register(data: Register, db: Session = Depends(get_db)):
    return register_function(db=db, name=data.name, email=data.email, number=data.number, pin=data.pin, password=data.password)

@auth_router.post('/reset-password/{email}')
async def request_reset_password(email: str, db: Session = Depends(get_db)):
    return await request_reset_password_function(email=email, db=db)

@auth_router.post('/reset-password/{email}/{otp}')
def validate_password(email: str, otp: str, db: Session = Depends(get_db)):
    return validate_otp_function(email=email, otp=otp, db=db)

@auth_router.post('/update-password/{email}/{token}')
def change_password(email: str, token: str, data: UpdatePassword, db: Session = Depends(get_db)):
    return change_password_function(email=email, token=token, new_password=data.new_password, confirm_new_password=data.confirm_new_password, db=db)