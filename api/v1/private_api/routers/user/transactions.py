from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.deps import get_current_user, get_db
from models.users import Services, User
from services.user.transactions import transaction_summary_function

user_transaction_router = APIRouter(
    prefix="/user/transaction",
    tags=['User Transaction']
)

@user_transaction_router.get("")
def transaction_summary(
    page: int = 1, 
    limit: int = 50,
    search: str = "",
    service: Literal[Services.DATA, Services.AIRTIME, Services.CABLE, Services.DISCO, Services.FUNDING] | None = None,
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
    ):
    return transaction_summary_function(user=user, db=db, search=search, service=service, page=page, limit=limit)