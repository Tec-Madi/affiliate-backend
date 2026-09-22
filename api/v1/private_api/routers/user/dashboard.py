from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user
from api.v1.private_api.schemas.user.dashboard import VerifyKYC
from core.database import get_db
from models.users import IDType, User
from services.user.dashboard import dashboard_function, view_bonus_details_function, withdraw_cashback_function
from services.user.verify_kyc import kyc_verification_function
from services.user.wallet import generate_account_function, get_virtual_accounts_function


dashboard_router = APIRouter(
    prefix='/user',
    tags=['User Dashboard']
)

@dashboard_router.get('/dashboard')
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return dashboard_function(user=user, db=db)

@dashboard_router.get('/bonus')
def view_bonus_detail(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return view_bonus_details_function(user=user, db=db)

@dashboard_router.post('/withdraw/bonus/{amount}')
def withdraw_cashback(amount: Decimal, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return withdraw_cashback_function(user=user, db=db, amount=amount)

@dashboard_router.post('/generate-account')
async def generate_account(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await generate_account_function(user=user, db=db)

@dashboard_router.get('/get-account')
def get_virtual_accounts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_virtual_accounts_function(user=user, db=db)

@dashboard_router.post('/verify-kyc/{id_type}')
async def kyc_verification(data: VerifyKYC, id_type: IDType, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await kyc_verification_function(user=user, db=db, id_type=id_type, id_number=data.id_number, number=data.number, date_of_birth=data.date_of_birth)